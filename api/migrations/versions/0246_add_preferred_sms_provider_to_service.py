"""

Revision ID: 0246
Revises: 0245
Create Date: 2020-06-15 16:49:07.113324

"""
from alembic import op
import sqlalchemy as sa


revision = '0246'
down_revision = '0245'


def upgrade():
    op.add_column('services', sa.Column('preferred_sms_provider', sa.String(), nullable=True))
    op.add_column('services_history', sa.Column('preferred_sms_provider', sa.String(), nullable=True))


def downgrade():
    op.drop_column('services_history', 'preferred_sms_provider')
    op.drop_column('services', 'preferred_sms_provider')
