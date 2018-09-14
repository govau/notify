"""

Revision ID: 0191_add_provider_details
Revises: 0190_change_templates_to_dta
Create Date: 2018-07-11 14:43:28.705904

"""
from alembic import op
from sqlalchemy.dialects import postgresql
from datetime import datetime
import uuid

revision = '0191_add_provider_details'
down_revision = '0190_change_templates_to_dta'


def upgrade():
    op.execute(
        "INSERT INTO provider_details (id, display_name, identifier, priority, notification_type, active, version) values ('{}', 'Telstra', 'telstra', 10, 'sms', true, 1)".format(
            str(uuid.uuid4())
        )
    )
    op.execute(
        (
            "INSERT INTO provider_rates (id, valid_from, rate, provider_id) VALUES ('{}', '{}', 1.8, "
            "(SELECT id FROM provider_details WHERE identifier = 'telstra'))"
        ).format(uuid.uuid4(), datetime.utcnow())
    )

    op.execute(
        "INSERT INTO provider_details (id, display_name, identifier, priority, notification_type, active, version) values ('{}', 'SMTP', 'smtp', 10, 'email', true, 1)".format(
            str(uuid.uuid4())
        )
    )
    op.execute(
        (
            "INSERT INTO provider_rates (id, valid_from, rate, provider_id) VALUES ('{}', '{}', 1.8, "
            "(SELECT id FROM provider_details WHERE identifier = 'smtp'))"
        ).format(uuid.uuid4(), datetime.utcnow())
    )


def downgrade():
    op.execute(
        """
    DELETE FROM provider_rates WHERE provider_id IN (
        SELECT * FROM (
            SELECT id FROM provider_details WHERE identifier = 'smtp'
        ) AS p
    )
"""
    )
    op.execute("DELETE FROM provider_details WHERE identifier = 'smtp'")

    op.execute(
        """
    DELETE FROM provider_rates WHERE provider_id IN (
        SELECT * FROM (
            SELECT id FROM provider_details WHERE identifier = 'telstra'
        ) AS p
    )
"""
    )
    op.execute("DELETE FROM provider_details WHERE identifier = 'telstra'")
