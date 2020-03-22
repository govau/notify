"""

Revision ID: 0239
Revises: 0238
Create Date: 2019-11-29 13:45:49.936809

"""
from alembic import op
from datetime import datetime
import uuid


revision = '0239'
down_revision = '0238'


def upgrade():
    op.execute("""
    DELETE FROM provider_statistics WHERE provider_id IN (
        SELECT * FROM (
            SELECT id FROM provider_details WHERE identifier = 'mmg' OR identifier = 'firetext' OR identifier = 'loadtesting'
        ) AS p
    )
""")

    op.execute("""
    DELETE FROM provider_rates WHERE provider_id IN (
        SELECT * FROM (
            SELECT id FROM provider_details WHERE identifier = 'mmg' OR identifier = 'firetext' OR identifier = 'loadtesting'
        ) AS p
    )
""")

    op.execute("DELETE FROM provider_details WHERE identifier = 'mmg' OR identifier = 'firetext' OR identifier = 'loadtesting'")

    op.execute("DELETE FROM provider_details_history where identifier = 'mmg' OR identifier = 'firetext' OR identifier = 'loadtesting'")


def downgrade():
    # MMG
    op.execute(
        "INSERT INTO provider_details (id, display_name, identifier, priority, notification_type, active, supports_international, version) values ('{}', 'MMG', 'mmg', 20, 'sms', false, false, 1)".format(str(uuid.uuid4()))
    )

    op.execute((
        "INSERT INTO provider_rates (id, valid_from, rate, provider_id) VALUES ('{}', '{}', 1.8, "
        "(SELECT id FROM provider_details WHERE identifier = 'mmg'))").format(uuid.uuid4(), datetime.utcnow()))

    op.execute(
        """
        INSERT INTO provider_details_history (id, display_name, identifier, priority, notification_type, active, supports_international, version)
        SELECT id, display_name, identifier, priority, notification_type, active, supports_international, version FROM provider_details WHERE identifier = 'mmg'
        """
    )

    # Firetext
    op.execute(
        "INSERT INTO provider_details (id, display_name, identifier, priority, notification_type, active, supports_international, version) values ('{}', 'Firetext', 'firetext', 20, 'sms', false, false, 1)".format(str(uuid.uuid4()))
    )

    op.execute((
        "INSERT INTO provider_rates (id, valid_from, rate, provider_id) VALUES ('{}', '{}', 2.5, "
        "(SELECT id FROM provider_details WHERE identifier = 'firetext'))").format(uuid.uuid4(), datetime.utcnow()))

    op.execute(
        """
        INSERT INTO provider_details_history (id, display_name, identifier, priority, notification_type, active, supports_international, version)
        SELECT id, display_name, identifier, priority, notification_type, active, supports_international, version FROM provider_details WHERE identifier = 'firetext'
        """
    )

    # Load testing
    op.execute(
        "INSERT INTO provider_details (id, display_name, identifier, priority, notification_type, active, supports_international, version) values ('{}', 'Loadtesting', 'loadtesting', 30, 'sms', true, false, 1)".format(str(uuid.uuid4()))
    )

    op.execute((
        "INSERT INTO provider_rates (id, valid_from, rate, provider_id) VALUES ('{}', '{}', 2.5, "
        "(SELECT id FROM provider_details WHERE identifier = 'loadtesting'))").format(uuid.uuid4(), datetime.utcnow()))

    op.execute(
        """
        INSERT INTO provider_details_history (id, display_name, identifier, priority, notification_type, active, supports_international, version)
        SELECT id, display_name, identifier, priority, notification_type, active, supports_international, version FROM provider_details WHERE identifier = 'loadtesting'
        """
    )
