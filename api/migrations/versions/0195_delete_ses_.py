"""

Revision ID: 0195_delete_ses
Revises: 0194_service_sms_senders
Create Date: 2018-07-16 11:42:09.321302

"""

import uuid

from alembic import op
from sqlalchemy.dialects import postgresql

revision = '0195_delete_ses'
down_revision = '0194_service_sms_senders'


def upgrade():
    op.execute("DELETE FROM provider_details_history where identifier = 'ses'")
    op.execute("DELETE FROM provider_details where identifier = 'ses'")


def downgrade():
    id = str(uuid.uuid4())
    op.execute(
        """
        INSERT INTO provider_details_history (id, display_name, identifier, priority, notification_type, active, version)
        VALUES ('{}', 'AWS SES', 'ses', 10, 'email', true, 1)
        """.format(
            id
        )
    )
    op.execute(
        """
        INSERT INTO provider_details (id, display_name, identifier, priority, notification_type, active, version)
        VALUES ('{}', 'AWS SES', 'ses', 10, 'email', true, 1)
        """.format(
            id
        )
    )
