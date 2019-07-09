"""

Revision ID: 0227
Revises: 0226
Create Date: 2019-07-09 15:39:25.569097

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0227'
down_revision = '0226'


def upgrade():
    op.add_column('invited_users', sa.Column('folder_permissions', postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), nullable=True))


def downgrade():
    op.drop_column('invited_users', 'folder_permissions')
