"""

Revision ID: 0211
Revises: 0210
Create Date: 2019-05-24 10:55:26.281561

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0211'
down_revision = '0210'


def upgrade():
    op.add_column('services', sa.Column('go_live_at', sa.DateTime(), nullable=True))
    op.add_column('services', sa.Column('go_live_user_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_services_go_live_user', 'services', 'users', ['go_live_user_id'], ['id'])
    op.add_column('services_history', sa.Column('go_live_at', sa.DateTime(), nullable=True))
    op.add_column('services_history', sa.Column('go_live_user_id', postgresql.UUID(as_uuid=True), nullable=True))


def downgrade():
    op.drop_column('services_history', 'go_live_user_id')
    op.drop_column('services_history', 'go_live_at')
    op.drop_constraint('fk_services_go_live_user', 'services', type_='foreignkey')
    op.drop_column('services', 'go_live_user_id')
    op.drop_column('services', 'go_live_at')
