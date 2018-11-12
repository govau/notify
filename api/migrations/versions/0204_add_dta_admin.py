"""

Revision ID: 0204
Revises: 0203
Create Date: 2018-11-12 14:23:45.808597

"""
from alembic import op
import sqlalchemy as sa

revision = '0204'
down_revision = '0203'

def upgrade():
    op.execute("UPDATE users SET platform_admin = true WHERE id = 'cf2f59b9-b092-4d30-a081-585b868aa76a'")

def downgrade():
    op.execute("UPDATE users SET platform_admin = false WHERE id = 'cf2f59b9-b092-4d30-a081-585b868aa76a'")
