"""

Revision ID: 0249
Revises: 0248
Create Date: 2020-09-24 17:32:30.470264

"""
from alembic import op
import sqlalchemy as sa


revision = '0249'
down_revision = '0248'


def upgrade():
    op.create_index(op.f('ix_callback_failures_notification_api_key_id'), 'callback_failures', ['notification_api_key_id'], unique=False)
    op.create_index(op.f('ix_callback_failures_callback_attempt_started'), 'callback_failures', ['callback_attempt_started'], unique=False)
    op.create_index(op.f('ix_callback_failures_callback_attempt_ended'), 'callback_failures', ['callback_attempt_ended'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_callback_failures_callback_attempt_ended'), table_name='callback_failures')
    op.drop_index(op.f('ix_callback_failures_callback_attempt_started'), table_name='callback_failures')
    op.drop_index(op.f('ix_callback_failures_notification_api_key_id'), table_name='callback_failures')
