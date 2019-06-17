"""

Revision ID: 0221
Revises: 0220
Create Date: 2019-05-29 10:25:18.234935

"""
from alembic import op
import sqlalchemy as sa


revision = '0221'
down_revision = '0220'


def upgrade():
    op.execute("INSERT INTO notification_status_types (name) VALUES ('cancelled')")
    op.execute("INSERT INTO notification_status_types (name) VALUES ('returned-letter')")
    op.execute("INSERT INTO notification_status_types (name) VALUES ('validation-failed')")


def downgrade():
    op.execute("UPDATE notifications SET notification_status = 'permanent-failure' WHERE notification_status = 'validation-failed'")
    op.execute("UPDATE notification_history SET notification_status = 'permanent-failure' WHERE notification_status = 'validation-failed'")
    op.execute("DELETE FROM notification_status_types WHERE name = 'validation-failed'")

    op.execute("DELETE FROM notification_status_types WHERE name='returned-letter'")
    op.execute("DELETE FROM notification_status_types WHERE name='cancelled'")
