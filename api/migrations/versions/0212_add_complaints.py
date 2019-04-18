"""

Revision ID: 0212
Revises: 0211
Create Date: 2019-04-18 13:41:53.875841

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0212'
down_revision = '0211'


def upgrade():
    op.create_table('complaints',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('notification_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('service_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('ses_feedback_id', sa.Text(), nullable=True),
    sa.Column('complaint_type', sa.Text(), nullable=True),
    sa.Column('complaint_date', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['notification_id'], ['notification_history.id'], ),
    sa.ForeignKeyConstraint(['service_id'], ['services.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_complaints_notification_id'), 'complaints', ['notification_id'], unique=False)
    op.create_index(op.f('ix_complaints_service_id'), 'complaints', ['service_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_complaints_service_id'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_notification_id'), table_name='complaints')
    op.drop_table('complaints')
