"""
Revision ID: 0214
Revises: 0213
Create Date: 2019-04-23 12:22:50.045233
"""
from alembic import op
import sqlalchemy as sa


revision = '0214'
down_revision = '0213'


def upgrade():
    op.execute("update service_callback_api set callback_type = 'delivery_status' where callback_type is null")


def downgrade():
    pass
