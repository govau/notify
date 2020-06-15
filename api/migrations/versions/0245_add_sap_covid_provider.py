"""

Revision ID: 0245
Revises: 0244
Create Date: 2020-06-15 16:36:55.264446

"""
from alembic import op
from datetime import datetime
import uuid


revision = '0245'
down_revision = '0244'


def upgrade():
    op.execute(
        "INSERT INTO provider_details (id, display_name, identifier, priority, notification_type, active, supports_international, version) values ('{}', 'SAP Covid', 'sap_covid', 99, 'sms', true, true, 1)".format(str(uuid.uuid4()))
    )

    op.execute((
        "INSERT INTO provider_rates (id, valid_from, rate, provider_id) VALUES ('{}', '{}', 6.0, "
        "(SELECT id FROM provider_details WHERE identifier = 'sap_covid'))").format(uuid.uuid4(), datetime.utcnow()))

    op.execute(
        """
        INSERT INTO provider_details_history (id, display_name, identifier, priority, notification_type, active, supports_international, version)
        SELECT id, display_name, identifier, priority, notification_type, active, supports_international, version FROM provider_details WHERE identifier = 'sap_covid'
        """
    )


def downgrade():
    op.execute("""
    DELETE FROM provider_rates WHERE provider_id IN (
        SELECT * FROM (
            SELECT id FROM provider_details WHERE identifier = 'sap_covid'
        ) AS p
    )
""")

    op.execute("DELETE FROM provider_details WHERE identifier = 'sap_covid'")

    op.execute("DELETE FROM provider_details_history where identifier = 'sap_covid'")
