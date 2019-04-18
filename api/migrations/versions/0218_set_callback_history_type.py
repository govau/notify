"""

Revision ID: 0218
Revises: 0217
Create Date: 2019-05-29 10:14:15.304702

"""
from alembic import op
import sqlalchemy as sa


revision = '0218'
down_revision = '0217'


def upgrade():
    op.execute("update service_callback_api_history set callback_type = 'delivery_status' where callback_type is null")


def downgrade():
    pass
