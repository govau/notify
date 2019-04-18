"""

Revision ID: 0211
Revises: 0210
Create Date: 2019-04-18 10:27:41.614756

"""
from alembic import op
import sqlalchemy as sa
import uuid

revision = '0211'
down_revision = '0210'


def upgrade():
    id = str(uuid.uuid4())
    op.execute(
        """
        INSERT INTO provider_details_history (id, display_name, identifier, priority, notification_type, active, version)
        VALUES ('{}', 'AWS SES', 'ses', 5, 'email', true, 1)
        """.format(id)
    )
    op.execute(
        """
        INSERT INTO provider_details (id, display_name, identifier, priority, notification_type, active, version)
        VALUES ('{}', 'AWS SES', 'ses', 5, 'email', true, 1)
        """.format(id)
    )


def downgrade():
    op.execute("DELETE FROM provider_details where identifier = 'ses'")
    op.execute("DELETE FROM provider_details_history where identifier = 'ses'")
