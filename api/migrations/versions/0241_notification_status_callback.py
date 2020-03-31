"""

Revision ID: 0241
Revises: 0240
Create Date: 2020-03-31 15:05:50.972829

"""
from alembic import op
import sqlalchemy as sa


revision = '0241'
down_revision = '0240'


def upgrade():
    op.add_column('notifications', sa.Column('status_callback_url', sa.String(), nullable=True))
    op.add_column('notifications', sa.Column('status_callback_bearer_token', sa.String(), nullable=True))


def downgrade():
    op.drop_column('notifications', 'status_callback_bearer_token')
    op.drop_column('notifications', 'status_callback_url')
