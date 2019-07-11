"""

Revision ID: 0231
Revises: 0230
Create Date: 2019-07-11 12:09:40.833198

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0231'
down_revision = '0230'


def upgrade():
    op.create_table('ft_notification_status',
                    sa.Column('aet_date', sa.Date(), nullable=False),
                    sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
                    sa.Column('service_id', postgresql.UUID(as_uuid=True), nullable=False),
                    sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
                    sa.Column('notification_type', sa.Text(), nullable=False),
                    sa.Column('key_type', sa.Text(), nullable=False),
                    sa.Column('notification_status', sa.Text(), nullable=False),
                    sa.Column('notification_count', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('aet_date', 'template_id', 'service_id', 'job_id', 'notification_type', 'key_type', 'notification_status')
                    )
    op.create_index(op.f('ix_ft_notification_status_aet_date'), 'ft_notification_status', ['aet_date'], unique=False)
    op.create_index(op.f('ix_ft_notification_status_job_id'), 'ft_notification_status', ['job_id'], unique=False)
    op.create_index(op.f('ix_ft_notification_status_service_id'), 'ft_notification_status', ['service_id'], unique=False)
    op.create_index(op.f('ix_ft_notification_status_template_id'), 'ft_notification_status', ['template_id'], unique=False)

    op.add_column('ft_notification_status', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('ft_notification_status', sa.Column('updated_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('ft_notification_status', 'updated_at')
    op.drop_column('ft_notification_status', 'created_at')

    op.drop_index(op.f('ix_ft_notification_status_aet_date'), table_name='ft_notification_status')
    op.drop_index(op.f('ix_ft_notification_status_template_id'), table_name='ft_notification_status')
    op.drop_index(op.f('ix_ft_notification_status_service_id'), table_name='ft_notification_status')
    op.drop_index(op.f('ix_ft_notification_status_job_id'), table_name='ft_notification_status')
    op.drop_table('ft_notification_status')
