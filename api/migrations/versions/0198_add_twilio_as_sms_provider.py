"""

Revision ID: 0198
Revises: 0197
Create Date: 2018-08-28 17:23:35.137724

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
import uuid


revision = '0198'
down_revision = '0197'

def upgrade():
    op.execute(
        "INSERT INTO provider_details (id, display_name, identifier, priority, notification_type, active, version) values ('{}', 'Twilio', 'twilio', 10, 'sms', true, 1)".format(str(uuid.uuid4()))
    )

    op.execute((
        "INSERT INTO provider_rates (id, valid_from, rate, provider_id) VALUES ('{}', '{}', 1.8, "
        "(SELECT id FROM provider_details WHERE identifier = 'twilio'))").format(uuid.uuid4(), datetime.utcnow()))

    op.execute(
        """
        INSERT INTO provider_details_history (id, display_name, identifier, priority, notification_type, active, version)
        SELECT id, display_name, identifier, priority, notification_type, active, version FROM provider_details WHERE identifier = 'twilio'
        """
    )


def downgrade():
    op.execute("""
    DELETE FROM provider_rates WHERE provider_id IN (
        SELECT * FROM (
            SELECT id FROM provider_details WHERE identifier = 'twilio'
        ) AS p
    )
""")

    op.execute("DELETE FROM provider_details WHERE identifier = 'twilio'")

    op.execute("DELETE FROM provider_details_history where identifier = 'twilio'")
