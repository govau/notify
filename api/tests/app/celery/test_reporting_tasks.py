from datetime import datetime, timedelta, date
from decimal import Decimal

import pytest
from freezegun import freeze_time

from tests.app.conftest import sample_notification
from app.celery.reporting_tasks import create_nightly_billing, get_rate, create_nightly_notification_status
from app.models import (
    FactBilling,
    Notification,
    LETTER_TYPE,
    EMAIL_TYPE,
    SMS_TYPE, FactNotificationStatus
)

from app.dao.letter_rate_dao import dao_create_letter_rate
from app.models import LetterRate, Rate
from app import db

from sqlalchemy import desc
from app.utils import convert_utc_to_aet

from tests.app.db import create_service, create_template, create_notification


def test_reporting_should_have_decorated_tasks_functions():
    assert create_nightly_billing.__wrapped__.__name__ == 'create_nightly_billing'


def mocker_get_rate(non_letter_rates, letter_rates, notification_type, date, crown=None, rate_multiplier=None):
    if notification_type == LETTER_TYPE:
        return Decimal(2.1)
    elif notification_type == SMS_TYPE:
        return Decimal(1.33)
    elif notification_type == EMAIL_TYPE:
        return Decimal(0)


@pytest.mark.parametrize('second_rate, records_num, billable_units, multiplier',
                         [(1.0, 1, 2, [1]),
                          (2.0, 2, 1, [1, 2])])
def test_create_nightly_billing_sms_rate_multiplier(
        notify_db,
        notify_db_session,
        sample_service,
        sample_template,
        mocker,
        second_rate,
        records_num,
        billable_units,
        multiplier):

    yesterday = datetime.utcnow() - timedelta(days=1)

    mocker.patch('app.celery.reporting_tasks.get_rate', side_effect=mocker_get_rate)

    # These are sms notifications
    sample_notification(
        notify_db,
        notify_db_session,
        created_at=yesterday,
        service=sample_service,
        template=sample_template,
        status='delivered',
        sent_by='twilio',
        international=False,
        rate_multiplier=1.0,
        billable_units=1,
    )
    sample_notification(
        notify_db,
        notify_db_session,
        created_at=yesterday,
        service=sample_service,
        template=sample_template,
        status='delivered',
        sent_by='twilio',
        international=False,
        rate_multiplier=second_rate,
        billable_units=1,
    )

    records = FactBilling.query.all()
    assert len(records) == 0

    create_nightly_billing()
    records = FactBilling.query.order_by('rate_multiplier').all()
    assert len(records) == records_num

    for i, record in enumerate(records):
        assert record.aet_date == datetime.date(convert_utc_to_aet(yesterday))
        assert record.rate == Decimal(1.33)
        assert record.billable_units == billable_units
        assert record.rate_multiplier == multiplier[i]


def test_create_nightly_billing_different_templates(
        notify_db,
        notify_db_session,
        sample_service,
        sample_template,
        sample_email_template,
        mocker):
    yesterday = datetime.utcnow() - timedelta(days=1)

    mocker.patch('app.celery.reporting_tasks.get_rate', side_effect=mocker_get_rate)

    sample_notification(
        notify_db,
        notify_db_session,
        created_at=yesterday,
        service=sample_service,
        template=sample_template,
        status='delivered',
        sent_by='twilio',
        international=False,
        rate_multiplier=1.0,
        billable_units=1,
    )
    sample_notification(
        notify_db,
        notify_db_session,
        created_at=yesterday,
        service=sample_service,
        template=sample_email_template,
        status='delivered',
        sent_by='ses',
        international=False,
        rate_multiplier=0,
        billable_units=0,
    )

    records = FactBilling.query.all()
    assert len(records) == 0

    create_nightly_billing()
    records = FactBilling.query.order_by('rate_multiplier').all()

    assert len(records) == 2
    multiplier = [0, 1]
    billable_units = [0, 1]
    rate = [0, Decimal(1.33)]
    for i, record in enumerate(records):
        assert record.aet_date == datetime.date(convert_utc_to_aet(yesterday))
        assert record.rate == rate[i]
        assert record.billable_units == billable_units[i]
        assert record.rate_multiplier == multiplier[i]


def test_create_nightly_billing_different_sent_by(
        notify_db,
        notify_db_session,
        sample_service,
        sample_template,
        sample_email_template,
        mocker):
    yesterday = datetime.utcnow() - timedelta(days=1)

    mocker.patch('app.celery.reporting_tasks.get_rate', side_effect=mocker_get_rate)

    # These are sms notifications
    sample_notification(
        notify_db,
        notify_db_session,
        created_at=yesterday,
        service=sample_service,
        template=sample_template,
        status='delivered',
        sent_by='telstra',
        international=False,
        rate_multiplier=1.0,
        billable_units=1,
    )
    sample_notification(
        notify_db,
        notify_db_session,
        created_at=yesterday,
        service=sample_service,
        template=sample_template,
        status='delivered',
        sent_by='twilio',
        international=False,
        rate_multiplier=1.0,
        billable_units=1,
    )

    records = FactBilling.query.all()
    assert len(records) == 0

    create_nightly_billing()
    records = FactBilling.query.order_by('rate_multiplier').all()

    assert len(records) == 2
    for i, record in enumerate(records):
        assert record.aet_date == datetime.date(convert_utc_to_aet(yesterday))
        assert record.rate == Decimal(1.33)
        assert record.billable_units == 1
        assert record.rate_multiplier == 1.0


def test_create_nightly_billing_letter(
        notify_db,
        notify_db_session,
        sample_service,
        sample_letter_template,
        mocker):
    yesterday = datetime.utcnow() - timedelta(days=1)

    mocker.patch('app.celery.reporting_tasks.get_rate', side_effect=mocker_get_rate)

    sample_notification(
        notify_db,
        notify_db_session,
        created_at=yesterday,
        service=sample_service,
        template=sample_letter_template,
        status='delivered',
        sent_by='dvla',
        international=False,
        rate_multiplier=2.0,
        billable_units=2,
    )

    records = FactBilling.query.all()
    assert len(records) == 0

    create_nightly_billing()
    records = FactBilling.query.order_by('rate_multiplier').all()
    assert len(records) == 1
    record = records[0]
    assert record.notification_type == LETTER_TYPE
    assert record.aet_date == datetime.date(convert_utc_to_aet(yesterday))
    assert record.rate == Decimal(2.1)
    assert record.billable_units == 2
    assert record.rate_multiplier == 2.0


def test_create_nightly_billing_null_sent_by_sms(
        notify_db,
        notify_db_session,
        sample_service,
        sample_template,
        mocker):
    yesterday = datetime.utcnow() - timedelta(days=1)

    mocker.patch('app.celery.reporting_tasks.get_rate', side_effect=mocker_get_rate)

    sample_notification(
        notify_db,
        notify_db_session,
        created_at=yesterday,
        service=sample_service,
        template=sample_template,
        status='delivered',
        sent_by=None,
        international=False,
        rate_multiplier=1.0,
        billable_units=1,
    )

    records = FactBilling.query.all()
    assert len(records) == 0

    create_nightly_billing()
    records = FactBilling.query.all()

    assert len(records) == 1
    record = records[0]
    assert record.aet_date == datetime.date(convert_utc_to_aet(yesterday))
    assert record.rate == Decimal(1.33)
    assert record.billable_units == 1
    assert record.rate_multiplier == 1
    assert record.provider == 'unknown'


@freeze_time('2018-01-15T03:30:00')
def test_create_nightly_billing_consolidate_from_3_days_delta(
        notify_db,
        notify_db_session,
        sample_service,
        sample_template,
        mocker):

    mocker.patch('app.celery.reporting_tasks.get_rate', side_effect=mocker_get_rate)

    # create records from 11th to 15th
    for i in range(0, 5):
        sample_notification(
            notify_db,
            notify_db_session,
            created_at=datetime.now() - timedelta(days=i),
            service=sample_service,
            template=sample_template,
            status='delivered',
            sent_by=None,
            international=False,
            rate_multiplier=1.0,
            billable_units=1,
        )

    notification = Notification.query.order_by(Notification.created_at).all()
    assert datetime.date(notification[0].created_at) == date(2018, 1, 11)

    records = FactBilling.query.all()
    assert len(records) == 0

    create_nightly_billing()
    records = FactBilling.query.order_by(FactBilling.aet_date).all()

    assert len(records) == 3
    assert records[0].aet_date == date(2018, 1, 12)
    assert records[-1].aet_date == date(2018, 1, 14)


def test_get_rate_for_letter_latest(notify_db, notify_db_session):
    letter_rate = LetterRate(start_date=datetime(2017, 12, 1),
                             rate=Decimal(0.33),
                             crown=True,
                             sheet_count=1,
                             post_class='second')

    dao_create_letter_rate(letter_rate)
    letter_rate = LetterRate(start_date=datetime(2016, 12, 1),
                             end_date=datetime(2017, 12, 1),
                             rate=Decimal(0.30),
                             crown=True,
                             sheet_count=1,
                             post_class='second')
    dao_create_letter_rate(letter_rate)

    non_letter_rates = [(r.notification_type, r.valid_from, r.rate) for r in
                        Rate.query.order_by(desc(Rate.valid_from)).all()]
    letter_rates = [(r.start_date, r.crown, r.sheet_count, r.rate) for r in
                    LetterRate.query.order_by(desc(LetterRate.start_date)).all()]

    rate = get_rate(non_letter_rates, letter_rates, LETTER_TYPE, datetime(2018, 1, 1), True, 1)
    assert rate == Decimal(0.33)


def test_get_rate_for_sms_and_email(notify_db, notify_db_session):
    letter_rate = LetterRate(start_date=datetime(2017, 12, 1),
                             rate=Decimal(0.33),
                             crown=True,
                             sheet_count=1,
                             post_class='second')
    dao_create_letter_rate(letter_rate)
    sms_rate = Rate(valid_from=datetime(2017, 12, 1),
                    rate=Decimal(0.15),
                    notification_type=SMS_TYPE)
    db.session.add(sms_rate)
    email_rate = Rate(valid_from=datetime(2017, 12, 1),
                      rate=Decimal(0),
                      notification_type=EMAIL_TYPE)
    db.session.add(email_rate)

    non_letter_rates = [(r.notification_type, r.valid_from, r.rate) for r in
                        Rate.query.order_by(desc(Rate.valid_from)).all()]
    letter_rates = [(r.start_date, r.crown, r.sheet_count, r.rate) for r in
                    LetterRate.query.order_by(desc(LetterRate.start_date)).all()]

    rate = get_rate(non_letter_rates, letter_rates, SMS_TYPE, datetime(2018, 1, 1))
    assert rate == Decimal(0.15)

    rate = get_rate(non_letter_rates, letter_rates, EMAIL_TYPE, datetime(2018, 1, 1))
    assert rate == Decimal(0)


@freeze_time('2018-10-09T13:30:00')  # 10/10/2018 00:30:00 AEDT
# Note: daylight savings time starts on 2018-10-07
def test_create_nightly_billing_use_aet(
        notify_db,
        notify_db_session,
        sample_service,
        sample_template,
        mocker):

    mocker.patch('app.celery.reporting_tasks.get_rate', side_effect=mocker_get_rate)

    sample_notification(
        notify_db,
        notify_db_session,
        created_at=datetime(2018, 10, 6, 14, 30),  # 07/10/2018 00:30:00 AEDT
        service=sample_service,
        template=sample_template,
        status='delivered',
        sent_by=None,
        international=False,
        rate_multiplier=1.0,
        billable_units=1,
    )

    sample_notification(
        notify_db,
        notify_db_session,
        created_at=datetime(2018, 10, 7, 13, 30),  # 08/10/2018 00:30:00 AEDT
        service=sample_service,
        template=sample_template,
        status='delivered',
        sent_by=None,
        international=False,
        rate_multiplier=1.0,
        billable_units=1,
    )

    notifications = Notification.query.order_by(Notification.created_at).all()
    assert len(notifications) == 2
    records = FactBilling.query.all()
    assert len(records) == 0

    create_nightly_billing()
    records = FactBilling.query.order_by(FactBilling.aet_date).all()

    assert len(records) == 2
    # The first record's aet_date is 06/10/2018. This is because the current
    # time is 2018-10-09T13:30:00 UTC, and 3 days earlier than that is
    # 2018-10-06T13:30:00 UTC which is 06/10/2018 23:30:00 AEST. This falls
    # outside of daylight savings time and so the aet_date is the 6th, not the
    # 7th.
    assert records[0].aet_date == date(2018, 10, 6)
    assert records[-1].aet_date == date(2018, 10, 8)


@freeze_time('2018-01-15T03:30:00')
def test_create_nightly_billing_update_when_record_exists(
        notify_db,
        notify_db_session,
        sample_service,
        sample_template,
        mocker):

    mocker.patch('app.celery.reporting_tasks.get_rate', side_effect=mocker_get_rate)

    sample_notification(
        notify_db,
        notify_db_session,
        created_at=datetime.now() - timedelta(days=1),
        service=sample_service,
        template=sample_template,
        status='delivered',
        sent_by=None,
        international=False,
        rate_multiplier=1.0,
        billable_units=1,
    )

    records = FactBilling.query.all()
    assert len(records) == 0

    create_nightly_billing()
    records = FactBilling.query.order_by(FactBilling.aet_date).all()

    assert len(records) == 1
    assert records[0].aet_date == date(2018, 1, 14)

    # run again, make sure create_nightly_billing updates with no error
    create_nightly_billing()
    assert len(records) == 1


def test_create_nightly_notification_status(notify_db_session):
    first_service = create_service(service_name='First Service')
    first_template = create_template(service=first_service)
    second_service = create_service(service_name='second Service')
    second_template = create_template(service=second_service, template_type='email')
    third_service = create_service(service_name='third Service')
    third_template = create_template(service=third_service, template_type='letter')

    create_notification(template=first_template, status='delivered')
    create_notification(template=first_template, status='delivered', created_at=datetime.utcnow() - timedelta(days=1))
    create_notification(template=first_template, status='delivered', created_at=datetime.utcnow() - timedelta(days=2))
    create_notification(template=first_template, status='delivered', created_at=datetime.utcnow() - timedelta(days=4))
    create_notification(template=first_template, status='delivered', created_at=datetime.utcnow() - timedelta(days=5))

    create_notification(template=second_template, status='temporary-failure')
    create_notification(template=second_template, status='temporary-failure',
                        created_at=datetime.utcnow() - timedelta(days=1))
    create_notification(template=second_template, status='temporary-failure',
                        created_at=datetime.utcnow() - timedelta(days=2))
    create_notification(template=second_template, status='temporary-failure',
                        created_at=datetime.utcnow() - timedelta(days=4))
    create_notification(template=second_template, status='temporary-failure',
                        created_at=datetime.utcnow() - timedelta(days=5))

    create_notification(template=third_template, status='created')
    create_notification(template=third_template, status='created', created_at=datetime.utcnow() - timedelta(days=1))
    create_notification(template=third_template, status='created', created_at=datetime.utcnow() - timedelta(days=2))
    create_notification(template=third_template, status='created', created_at=datetime.utcnow() - timedelta(days=4))
    create_notification(template=third_template, status='created', created_at=datetime.utcnow() - timedelta(days=5))

    assert len(FactNotificationStatus.query.all()) == 0

    create_nightly_notification_status()
    new_data = FactNotificationStatus.query.order_by(
        FactNotificationStatus.aet_date,
        FactNotificationStatus.notification_type
    ).all()
    assert len(new_data) == 9
    assert str(new_data[0].aet_date) == datetime.strftime(convert_utc_to_aet(datetime.utcnow() - timedelta(days=4)), "%Y-%m-%d")
    assert str(new_data[3].aet_date) == datetime.strftime(convert_utc_to_aet(datetime.utcnow() - timedelta(days=2)), "%Y-%m-%d")
    assert str(new_data[6].aet_date) == datetime.strftime(convert_utc_to_aet(datetime.utcnow() - timedelta(days=1)), "%Y-%m-%d")


@freeze_time('2019-10-20 13:30')  # 21 October 2019 12:30am AEDT
def test_create_nightly_notification_status_respects_aet(sample_template):
    create_notification(sample_template, status='delivered', created_at=datetime(2019, 10, 20, 13, 0))  # too new

    create_notification(sample_template, status='created', created_at=datetime(2019, 10, 20, 12, 59))
    create_notification(sample_template, status='created', created_at=datetime(2019, 10, 19, 23, 0))

    create_notification(sample_template, status='temporary-failure', created_at=datetime(2019, 10, 19, 22, 59))

    # we create records for last four days
    create_notification(sample_template, status='sending', created_at=datetime(2019, 10, 17, 0, 0))

    create_notification(sample_template, status='delivered', created_at=datetime(2019, 3, 16, 23, 59))  # too old

    create_nightly_notification_status()

    noti_status = FactNotificationStatus.query.order_by(FactNotificationStatus.aet_date).all()
    assert len(noti_status) == 3

    assert noti_status[0].aet_date == date(2019, 10, 17)
    assert noti_status[0].notification_status == 'sending'

    assert noti_status[1].aet_date == date(2019, 10, 20)
    assert noti_status[1].notification_status == 'created'

    assert noti_status[2].aet_date == date(2019, 10, 20)
    assert noti_status[2].notification_status == 'temporary-failure'
