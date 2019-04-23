"""
Revision ID: 0215
Revises: 0214
Create Date: 2019-04-23 12:23:18.759838
"""
from alembic import op
import sqlalchemy as sa


revision = '0215'
down_revision = '0214'


def upgrade():
    op.execute("update service_callback_api_history set callback_type = 'delivery_status' where callback_type is null")


def downgrade():
    pass
