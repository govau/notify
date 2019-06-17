"""

Revision ID: 0217
Revises: 0216
Create Date: 2019-05-29 10:13:38.576348

"""
from alembic import op
import sqlalchemy as sa


revision = '0217'
down_revision = '0216'


def upgrade():
    op.execute("update service_callback_api set callback_type = 'delivery_status' where callback_type is null")


def downgrade():
    pass
