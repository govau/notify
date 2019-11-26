"""

Revision ID: 0238
Revises: 0237
Create Date: 2019-11-29 13:43:56.438399

"""
from alembic import op
from datetime import datetime
import uuid


revision = '0238'
down_revision = '0237'


def upgrade():
    op.execute(
        "INSERT INTO provider_details (id, display_name, identifier, priority, notification_type, active, supports_international, version) values ('{}', 'SAP', 'sap', 20, 'sms', true, true, 1)".format(str(uuid.uuid4()))
    )

    op.execute((
        "INSERT INTO provider_rates (id, valid_from, rate, provider_id) VALUES ('{}', '{}', 4.0, "
        "(SELECT id FROM provider_details WHERE identifier = 'sap'))").format(uuid.uuid4(), datetime.utcnow()))

    op.execute(
        """
        INSERT INTO provider_details_history (id, display_name, identifier, priority, notification_type, active, supports_international, version)
        SELECT id, display_name, identifier, priority, notification_type, active, supports_international, version FROM provider_details WHERE identifier = 'sap'
        """
    )


def downgrade():
    op.execute("""
    DELETE FROM provider_rates WHERE provider_id IN (
        SELECT * FROM (
            SELECT id FROM provider_details WHERE identifier = 'sap'
        ) AS p
    )
""")

    op.execute("DELETE FROM provider_details WHERE identifier = 'sap'")

    op.execute("DELETE FROM provider_details_history where identifier = 'sap'")
