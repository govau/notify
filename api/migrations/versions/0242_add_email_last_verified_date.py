"""

Revision ID: 0242
Revises: 0241
Create Date: 2020-05-21 12:16:17.119733

"""
from alembic import op
import sqlalchemy as sa


revision = '0242'
down_revision = '0241'


def upgrade():
    op.add_column('users', sa.Column('email_last_verified_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('users', 'email_last_verified_at')
