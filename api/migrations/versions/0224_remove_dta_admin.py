"""

Revision ID: 0224
Revises: 0223
Create Date: 2019-07-04 12:28:51.761753

"""
from alembic import op


revision = '0224'
down_revision = '0223'


def upgrade():
    op.execute("UPDATE users SET platform_admin = false WHERE id = 'cf2f59b9-b092-4d30-a081-585b868aa76a'")


def downgrade():
    op.execute("UPDATE users SET platform_admin = true WHERE id = 'cf2f59b9-b092-4d30-a081-585b868aa76a'")
