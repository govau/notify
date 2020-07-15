"""

Revision ID: 0248
Revises: 0247
Create Date: 2020-07-09 16:58:01.193221

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0248'
down_revision = '0247'


def upgrade():
    op.create_table('callback_failures',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('notification_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('service_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('service_callback_url', sa.Text(), nullable=False),
        sa.Column('notification_api_key_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notification_api_key_type', sa.String(length=255), nullable=True),
        sa.Column('callback_attempt_number', sa.Integer(), nullable=False),
        sa.Column('callback_attempt_started', sa.DateTime(), nullable=False),
        sa.Column('callback_attempt_ended', sa.DateTime(), nullable=False),
        sa.Column('callback_failure_type', sa.Text(), nullable=True),
        sa.Column('service_callback_type', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['notification_id'], ['notification_history.id']),
        sa.ForeignKeyConstraint(['service_id'], ['services.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_callback_failures_notification_id'), 'callback_failures', ['notification_id'], unique=False)
    op.create_index(op.f('ix_callback_failures_service_id'), 'callback_failures', ['service_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_callback_failures_service_id'), table_name='callback_failures')
    op.drop_index(op.f('ix_callback_failures_notification_id'), table_name='callback_failures')
    op.drop_table('callback_failures')
