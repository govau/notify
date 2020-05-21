import os
import secrets
import string
import uuid

from flask import _request_ctx_stack, request, g, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from monotonic import monotonic
from notifications_utils.clients import DeskproClient
from notifications_utils.clients.statsd.statsd_client import StatsdClient
from notifications_utils.clients.redis.redis_client import RedisClient
from notifications_utils import logging, request_helper
from werkzeug.local import LocalProxy

from app.celery.celery import NotifyCelery
from app.clients import Clients
from app.clients.email.smtp import SMTPClient
from app.clients.email.aws_ses import AwsSesClient
from app.clients.sms.sap import SAPSMSClient
from app.clients.sms.telstra import TelstraSMSClient
from app.clients.sms.twilio import TwilioSMSClient
from app.clients.performance_platform.performance_platform_client import PerformancePlatformClient
from app.encryption import Encryption

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
DATE_FORMAT = "%Y-%m-%d"

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
notify_celery = NotifyCelery()
sap_sms_client = SAPSMSClient(
    client_id=os.getenv('SAP_CLIENT_ID'),
    client_secret=os.getenv('SAP_CLIENT_SECRET'),
)
telstra_sms_client = TelstraSMSClient(
    client_id=os.getenv('TELSTRA_MESSAGING_CLIENT_ID'),
    client_secret=os.getenv('TELSTRA_MESSAGING_CLIENT_SECRET'),
)
twilio_sms_client = TwilioSMSClient(
    account_sid=os.getenv('TWILIO_ACCOUNT_SID'),
    auth_token=os.getenv('TWILIO_AUTH_TOKEN'),
    from_number=os.getenv('TWILIO_FROM_NUMBER'),
)
smtp_client = SMTPClient(
    addr=os.getenv('SMTP_ADDR'),
    user=os.getenv('SMTP_USER'),
    password=os.getenv('SMTP_PASSWORD'),
)
aws_ses_client = AwsSesClient()
encryption = Encryption()
deskpro_client = DeskproClient()
statsd_client = StatsdClient()
redis_store = RedisClient()
performance_platform_client = PerformancePlatformClient()

clients = Clients()

api_user = LocalProxy(lambda: _request_ctx_stack.top.api_user)
authenticated_service = LocalProxy(lambda: _request_ctx_stack.top.authenticated_service)


def create_app(application):
    from app.config import configs

    notify_environment = os.environ['NOTIFY_ENVIRONMENT']

    application.config.from_object(configs[notify_environment])

    application.config['NOTIFY_APP_NAME'] = application.name

    init_app(application)
    request_helper.init_app(application)
    db.init_app(application)
    migrate.init_app(application, db=db)
    ma.init_app(application)
    deskpro_client.init_app(application)
    statsd_client.init_app(application)
    logging.init_app(application, statsd_client)
    sap_sms_client.init_app(
        logger=application.logger,
        notify_host=application.config["API_HOST_NAME"]
    )
    telstra_sms_client.init_app(
        logger=application.logger,
        notify_host=application.config["API_HOST_NAME"]
    )
    twilio_sms_client.init_app(
        logger=application.logger,
        notify_host=application.config["API_HOST_NAME"],
        callback_username=application.config["TWILIO_CALLBACK_USERNAME"],
        callback_password=application.config["TWILIO_CALLBACK_PASSWORD"],
    )
    aws_ses_client.init_app(
        application.config['AWS_SES_REGION'],
        application.config['AWS_SES_ACCESS_KEY_ID'],
        application.config['AWS_SES_SECRET_ACCESS_KEY'],
        statsd_client=statsd_client
    )
    smtp_client.init_app(application, statsd_client=statsd_client)
    notify_celery.init_app(application)
    encryption.init_app(application)
    redis_store.init_app(application)
    performance_platform_client.init_app(application)
    clients.init_app(
        sms_clients=[sap_sms_client, telstra_sms_client, twilio_sms_client],
        email_clients=[aws_ses_client, smtp_client]
    )

    register_blueprint(application)
    register_v2_blueprints(application)

    # avoid circular imports by importing this file later
    from app.commands import setup_commands
    setup_commands(application)

    return application


def register_blueprint(application):
    from app.service.rest import service_blueprint
    from app.service.callback_rest import service_callback_blueprint
    from app.user.rest import user_blueprint
    from app.template.rest import template_blueprint
    from app.support.support import support as support_blueprint
    from app.status.healthcheck import status as status_blueprint
    from app.sap.routes import bp as sap_blueprint
    from app.sap.oauth2 import configure_oauth as sap_configure_oauth
    from app.job.rest import job_blueprint
    from app.notifications.rest import notifications as notifications_blueprint
    from app.invite.rest import invite as invite_blueprint
    from app.accept_invite.rest import accept_invite
    from app.template_statistics.rest import template_statistics as template_statistics_blueprint
    from app.events.rest import events as events_blueprint
    from app.provider_details.rest import provider_details as provider_details_blueprint
    from app.email_branding.rest import email_branding_blueprint
    from app.dvla_organisation.rest import dvla_organisation_blueprint
    from app.delivery.rest import delivery_blueprint
    from app.inbound_number.rest import inbound_number_blueprint
    from app.inbound_sms.rest import inbound_sms as inbound_sms_blueprint
    from app.notifications.receive_notifications import receive_notifications_blueprint
    from app.notifications.notifications_ses_callback import ses_callback_blueprint
    from app.notifications.notifications_sms_callback import sms_callback_blueprint
    from app.notifications.notifications_letter_callback import letter_callback_blueprint
    from app.authentication.auth import requires_admin_auth, requires_auth, requires_no_auth
    from app.letters.rest import letter_job
    from app.billing.rest import billing_blueprint
    from app.organisation.rest import organisation_blueprint
    from app.organisation.invite_rest import organisation_invite_blueprint
    from app.complaint.complaint_rest import complaint_blueprint
    from app.platform_stats.rest import platform_stats_blueprint

    service_blueprint.before_request(requires_admin_auth)
    application.register_blueprint(service_blueprint, url_prefix='/service')

    user_blueprint.before_request(requires_admin_auth)
    application.register_blueprint(user_blueprint, url_prefix='/user')

    template_blueprint.before_request(requires_admin_auth)
    application.register_blueprint(template_blueprint)

    support_blueprint.before_request(requires_no_auth)
    application.register_blueprint(support_blueprint)

    status_blueprint.before_request(requires_no_auth)
    application.register_blueprint(status_blueprint)

    sap_configure_oauth(application)
    sap_blueprint.before_request(requires_no_auth)
    application.register_blueprint(sap_blueprint)

    # delivery receipts
    ses_callback_blueprint.before_request(requires_no_auth)
    application.register_blueprint(ses_callback_blueprint)
    # TODO: make sure research mode can still trigger sms callbacks, then re-enable this
    sms_callback_blueprint.before_request(requires_no_auth)
    application.register_blueprint(sms_callback_blueprint)

    # inbound sms
    receive_notifications_blueprint.before_request(requires_no_auth)
    application.register_blueprint(receive_notifications_blueprint)

    notifications_blueprint.before_request(requires_auth)
    application.register_blueprint(notifications_blueprint)

    job_blueprint.before_request(requires_admin_auth)
    application.register_blueprint(job_blueprint)

    invite_blueprint.before_request(requires_admin_auth)
    application.register_blueprint(invite_blueprint)

    delivery_blueprint.before_request(requires_admin_auth)
    application.register_blueprint(delivery_blueprint)

    inbound_number_blueprint.before_request(requires_admin_auth)
    application.register_blueprint(inbound_number_blueprint)

    inbound_sms_blueprint.before_request(requires_admin_auth)
    application.register_blueprint(inbound_sms_blueprint)

    accept_invite.before_request(requires_admin_auth)
    application.register_blueprint(accept_invite, url_prefix='/invite')

    template_statistics_blueprint.before_request(requires_admin_auth)
    application.register_blueprint(template_statistics_blueprint)

    events_blueprint.before_request(requires_admin_auth)
    application.register_blueprint(events_blueprint)

    provider_details_blueprint.before_request(requires_admin_auth)
    application.register_blueprint(provider_details_blueprint, url_prefix='/provider-details')

    email_branding_blueprint.before_request(requires_admin_auth)
    application.register_blueprint(email_branding_blueprint, url_prefix='/email-branding')

    dvla_organisation_blueprint.before_request(requires_admin_auth)
    application.register_blueprint(dvla_organisation_blueprint, url_prefix='/dvla_organisations')

    letter_job.before_request(requires_admin_auth)
    application.register_blueprint(letter_job)

    letter_callback_blueprint.before_request(requires_no_auth)
    application.register_blueprint(letter_callback_blueprint)

    billing_blueprint.before_request(requires_admin_auth)
    application.register_blueprint(billing_blueprint)

    service_callback_blueprint.before_request(requires_admin_auth)
    application.register_blueprint(service_callback_blueprint)

    organisation_blueprint.before_request(requires_admin_auth)
    application.register_blueprint(organisation_blueprint, url_prefix='/organisations')

    organisation_invite_blueprint.before_request(requires_admin_auth)
    application.register_blueprint(organisation_invite_blueprint)

    complaint_blueprint.before_request(requires_admin_auth)
    application.register_blueprint(complaint_blueprint)

    platform_stats_blueprint.before_request(requires_admin_auth)
    application.register_blueprint(platform_stats_blueprint, url_prefix='/platform-stats')


def register_v2_blueprints(application):
    from app.v2.inbound_sms.get_inbound_sms import v2_inbound_sms_blueprint as get_inbound_sms
    from app.v2.notifications.post_notifications import v2_notification_blueprint as post_notifications
    from app.v2.notifications.get_notifications import v2_notification_blueprint as get_notifications
    from app.v2.template.get_template import v2_template_blueprint as get_template
    from app.v2.templates.get_templates import v2_templates_blueprint as get_templates
    from app.v2.template.post_template import v2_template_blueprint as post_template
    from app.authentication.auth import requires_auth

    post_notifications.before_request(requires_auth)
    application.register_blueprint(post_notifications)

    get_notifications.before_request(requires_auth)
    application.register_blueprint(get_notifications)

    get_templates.before_request(requires_auth)
    application.register_blueprint(get_templates)

    get_template.before_request(requires_auth)
    application.register_blueprint(get_template)

    post_template.before_request(requires_auth)
    application.register_blueprint(post_template)

    get_inbound_sms.before_request(requires_auth)
    application.register_blueprint(get_inbound_sms)


def init_app(app):
    @app.before_request
    def record_user_agent():
        statsd_client.incr("user-agent.{}".format(process_user_agent(request.headers.get('User-Agent', None))))

    @app.before_request
    def record_request_details():
        g.start = monotonic()
        g.endpoint = request.endpoint

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response

    @app.errorhandler(Exception)
    def exception(error):
        app.logger.exception(error)
        # error.code is set for our exception types.
        return jsonify(result='error', message=error.message), error.code or 500

    @app.errorhandler(404)
    def page_not_found(e):
        msg = e.description or "Not found"
        return jsonify(result='error', message=msg), 404


def create_uuid():
    return str(uuid.uuid4())


def create_random_identifier():
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16))


def process_user_agent(user_agent_string):
    if user_agent_string and user_agent_string.lower().startswith("notify"):
        components = user_agent_string.split("/")
        client_name = components[0].lower()
        client_version = components[1].replace(".", "-")
        return "{}.{}".format(client_name, client_version)
    elif user_agent_string and not user_agent_string.lower().startswith("notify"):
        return "non-notify-user-agent"
    else:
        return "unknown"
