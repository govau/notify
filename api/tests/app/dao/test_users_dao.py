from datetime import datetime, timedelta
import uuid

from freezegun import freeze_time
from sqlalchemy.exc import DataError
from sqlalchemy.orm.exc import NoResultFound
import pytest

from app import db
from app.dao.users_dao import (
    save_model_user,
    save_user_attribute,
    get_user_by_id,
    delete_model_user,
    increment_failed_login_count,
    reset_failed_login_count,
    get_user_by_email,
    delete_codes_older_created_more_than_a_day_ago,
    update_user_password,
    count_user_verify_codes,
    user_can_be_archived,
    dao_archive_user,
)
from app.errors import InvalidRequest
from app.models import EMAIL_AUTH_TYPE, User, VerifyCode

from tests.app.db import create_permissions, create_service, create_user


@pytest.mark.parametrize('phone_number', [
    '+61412345678',
    '+1-800-555-5555',
])
def test_create_user(notify_db_session, phone_number):
    email = 'notify@digital.cabinet-office.gov.uk'
    data = {
        'name': 'Test User',
        'email_address': email,
        'password': 'password',
        'mobile_number': phone_number
    }
    user = User(**data)
    save_model_user(user)
    assert User.query.count() == 1
    assert User.query.first().email_address == email
    assert User.query.first().id == user.id
    assert User.query.first().mobile_number == phone_number
    assert not user.platform_admin


def test_get_all_users(notify_db_session):
    create_user(email='1@test.com')
    create_user(email='2@test.com')

    assert User.query.count() == 2
    assert len(get_user_by_id()) == 2


def test_get_user(notify_db_session):
    email = '1@test.com'
    user = create_user(email=email)
    assert get_user_by_id(user_id=user.id).email_address == email


def test_get_user_not_exists(notify_db_session, fake_uuid):
    with pytest.raises(NoResultFound):
        get_user_by_id(user_id=fake_uuid)


def test_get_user_invalid_id(notify_db_session):
    with pytest.raises(DataError):
        get_user_by_id(user_id="blah")


def test_delete_users(sample_user):
    assert User.query.count() == 1
    delete_model_user(sample_user)
    assert User.query.count() == 0


def test_increment_failed_login_should_increment_failed_logins(sample_user):
    assert sample_user.failed_login_count == 0
    increment_failed_login_count(sample_user)
    assert sample_user.failed_login_count == 1


def test_reset_failed_login_should_set_failed_logins_to_0(sample_user):
    increment_failed_login_count(sample_user)
    assert sample_user.failed_login_count == 1
    reset_failed_login_count(sample_user)
    assert sample_user.failed_login_count == 0


def test_get_user_by_email(sample_user):
    user_from_db = get_user_by_email(sample_user.email_address)
    assert sample_user == user_from_db


def test_get_user_by_email_is_case_insensitive(sample_user):
    email = sample_user.email_address
    user_from_db = get_user_by_email(email.upper())
    assert sample_user == user_from_db


def test_should_delete_all_verification_codes_more_than_one_day_old(sample_user):
    make_verify_code(sample_user, age=timedelta(hours=24), code="54321")
    make_verify_code(sample_user, age=timedelta(hours=24), code="54321")
    assert VerifyCode.query.count() == 2
    delete_codes_older_created_more_than_a_day_ago()
    assert VerifyCode.query.count() == 0


def test_should_not_delete_verification_codes_less_than_one_day_old(sample_user):
    make_verify_code(sample_user, age=timedelta(hours=23, minutes=59, seconds=59), code="12345")
    make_verify_code(sample_user, age=timedelta(hours=24), code="54321")

    assert VerifyCode.query.count() == 2
    delete_codes_older_created_more_than_a_day_ago()
    assert VerifyCode.query.one()._code == "12345"


def make_verify_code(user, age=timedelta(hours=0), expiry_age=timedelta(0), code="12335", code_used=False):
    verify_code = VerifyCode(
        code_type='sms',
        _code=code,
        created_at=datetime.utcnow() - age,
        expiry_datetime=datetime.utcnow() - expiry_age,
        user=user,
        code_used=code_used
    )
    db.session.add(verify_code)
    db.session.commit()


@pytest.mark.parametrize('user_attribute, user_value', [
    ('name', 'New User'),
    ('email_address', 'newuser@mail.com'),
    ('mobile_number', '+4407800900460')
])
def test_update_user_attribute(client, sample_user, user_attribute, user_value):
    assert getattr(sample_user, user_attribute) != user_value
    update_dict = {
        user_attribute: user_value
    }
    save_user_attribute(sample_user, update_dict)
    assert getattr(sample_user, user_attribute) == user_value


def test_update_user_password(notify_api, notify_db, notify_db_session, sample_user):
    password = 'newpassword'
    assert not sample_user.check_password(password)
    update_user_password(sample_user, password)
    assert sample_user.check_password(password)


def test_count_user_verify_codes(sample_user):
    with freeze_time(datetime.utcnow() + timedelta(hours=1)):
        make_verify_code(sample_user, code_used=True)
        make_verify_code(sample_user, expiry_age=timedelta(hours=2))
        [make_verify_code(sample_user) for i in range(5)]

    assert count_user_verify_codes(sample_user) == 5


@freeze_time('2018-07-07 12:00:00')
def test_dao_archive_user(sample_user, sample_organisation, fake_uuid):
    sample_user.current_session_id = fake_uuid

    # create 2 services for sample_user to be a member of (each with another active user)
    service_1 = create_service(service_name='Service 1')
    service_1_user = create_user(email='1@test.com')
    service_1.users = [sample_user, service_1_user]
    create_permissions(sample_user, service_1, 'manage_settings')
    create_permissions(service_1_user, service_1, 'manage_settings', 'view_activity')

    service_2 = create_service(service_name='Service 2')
    service_2_user = create_user(email='2@test.com')
    service_2.users = [sample_user, service_2_user]
    create_permissions(sample_user, service_2, 'view_activity')
    create_permissions(service_2_user, service_2, 'manage_settings')

    # make sample_user an org member
    sample_organisation.users = [sample_user]

    dao_archive_user(sample_user)

    assert sample_user.get_permissions() == {}
    assert sample_user.services == []
    assert sample_user.organisations == []
    assert sample_user.auth_type == EMAIL_AUTH_TYPE
    assert sample_user.email_address == '_archived_2018-07-07_notify@digital.cabinet-office.gov.uk'
    assert sample_user.mobile_number is None
    assert sample_user.current_session_id == uuid.UUID('00000000-0000-0000-0000-000000000000')
    assert sample_user.state == 'inactive'
    assert not sample_user.check_password('password')


def test_user_can_be_archived_if_they_do_not_belong_to_any_services(sample_user):
    assert sample_user.services == []
    assert user_can_be_archived(sample_user)


def test_user_can_be_archived_if_they_do_not_belong_to_any_active_services(sample_user, sample_service):
    sample_user.services = [sample_service]
    sample_service.active = False

    assert len(sample_user.services) == 1
    assert user_can_be_archived(sample_user)


def test_user_can_be_archived_if_the_other_service_members_have_the_manage_settings_permission(sample_service):
    user_1 = create_user(email='1@test.com')
    user_2 = create_user(email='2@test.com')
    user_3 = create_user(email='3@test.com')

    sample_service.users = [user_1, user_2, user_3]

    create_permissions(user_1, sample_service, 'manage_settings')
    create_permissions(user_2, sample_service, 'manage_settings', 'view_activity')
    create_permissions(user_3, sample_service, 'manage_settings', 'send_emails', 'send_letters', 'send_texts')

    assert len(sample_service.users) == 3
    assert user_can_be_archived(user_1)


def test_dao_archive_user_raises_error_if_user_cannot_be_archived(sample_user, mocker):
    mocker.patch('app.dao.users_dao.user_can_be_archived', return_value=False)

    with pytest.raises(InvalidRequest):
        dao_archive_user(sample_user.id)


def test_user_cannot_be_archived_if_they_belong_to_a_service_with_no_other_active_users(sample_service):
    active_user = create_user(email='1@test.com')
    pending_user = create_user(email='2@test.com', state='pending')
    inactive_user = create_user(email='3@test.com', state='inactive')

    sample_service.users = [active_user, pending_user, inactive_user]

    assert len(sample_service.users) == 3
    assert not user_can_be_archived(active_user)


def test_user_cannot_be_archived_if_the_other_service_members_do_not_have_the_manage_setting_permission(
    sample_service,
):
    active_user = create_user(email='1@test.com')
    pending_user = create_user(email='2@test.com')
    inactive_user = create_user(email='3@test.com')

    sample_service.users = [active_user, pending_user, inactive_user]

    create_permissions(active_user, sample_service, 'manage_settings')
    create_permissions(pending_user, sample_service, 'view_activity')
    create_permissions(inactive_user, sample_service, 'send_emails', 'send_letters', 'send_texts')

    assert len(sample_service.users) == 3
    assert not user_can_be_archived(active_user)
