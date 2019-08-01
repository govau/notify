"""

Revision ID: 0234
Revises: 0233
Create Date: 2019-08-01 14:04:43.591503

"""
from alembic import op
import sqlalchemy as sa


revision = '0234'
down_revision = '0233'
admin_user_id = 'b4e6154c-235b-461d-9dea-774f9f7d610a'


def upgrade():
    op.execute(f"UPDATE users SET platform_admin = true WHERE id = '{admin_user_id}'")

def downgrade():
    op.execute(f"UPDATE users SET platform_admin = false WHERE id = '{admin_user_id}'")
