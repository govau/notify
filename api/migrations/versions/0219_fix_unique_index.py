"""

Revision ID: 0219
Revises: 0218
Create Date: 2019-05-29 10:14:48.742350

"""
from alembic import op
import sqlalchemy as sa


revision = '0219'
down_revision = '0218'


def upgrade():
    op.create_unique_constraint('uix_service_callback_type', 'service_callback_api', ['service_id', 'callback_type'])
    op.drop_index('ix_service_callback_api_service_id', table_name='service_callback_api')
    op.create_index(op.f('ix_service_callback_api_service_id'), 'service_callback_api', ['service_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_service_callback_api_service_id'), table_name='service_callback_api')
    op.create_index('ix_service_callback_api_service_id', 'service_callback_api', ['service_id'], unique=True)
    op.drop_constraint('uix_service_callback_type', 'service_callback_api', type_='unique')
