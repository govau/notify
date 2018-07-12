"""

Revision ID: 0193_add_provider_details_hist
Revises: 0192_change_email_from
Create Date: 2018-07-12 13:51:07.410048

"""
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '0193_add_provider_details_hist'
down_revision = '0192_change_email_from'


def upgrade():
    op.execute(
        """
        INSERT INTO provider_details_history (id, display_name, identifier, priority, notification_type, active, version)
        SELECT id, display_name, identifier, priority, notification_type, active, version FROM provider_details WHERE identifier = 'telstra'
        """
    )
    op.execute(
        """
        INSERT INTO provider_details_history (id, display_name, identifier, priority, notification_type, active, version)
        SELECT id, display_name, identifier, priority, notification_type, active, version FROM provider_details WHERE identifier = 'smtp'
        """
    )


def downgrade():
    op.execute("DELETE FROM provider_details_history where identifier = 'smtp'")
    op.execute("DELETE FROM provider_details_history where identifier = 'telstra'")
