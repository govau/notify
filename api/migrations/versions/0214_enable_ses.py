"""

Revision ID: 0214
Revises: 0213
Create Date: 2019-05-29 10:05:55.096758

"""
from alembic import op
import sqlalchemy as sa
import uuid


revision = '0214'
down_revision = '0213'


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
