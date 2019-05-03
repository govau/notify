"""

Revision ID: 0210
Revises: 209
Create Date: 2019-04-03 09:49:18.381768

"""
from alembic import op
import sqlalchemy as sa


revision = '0210'
down_revision = '209'


def upgrade():
    op.execute('ALTER TABLE users ADD COLUMN failed_verify_count integer NOT NULL default 0')


def downgrade():
    op.execute('ALTER TABLE users DROP COLUMN failed_verify_count')
