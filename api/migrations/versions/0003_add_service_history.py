"""empty message

Revision ID: 0003_add_service_history
Revises: 0002_add_content_char_count
Create Date: 2016-04-19 13:01:54.519821

"""

# revision identifiers, used by Alembic.
revision = '0003_add_service_history'
down_revision = '0002_add_content_char_count'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'services_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('message_limit', sa.BigInteger(), nullable=False),
        sa.Column('restricted', sa.Boolean(), nullable=False),
        sa.Column('email_from', sa.Text(), nullable=False),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version', sa.Integer(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('id', 'version'),
    )
    op.create_index(
        op.f('ix_services_history_created_by_id'),
        'services_history',
        ['created_by_id'],
        unique=False,
    )
    op.add_column(
        'services',
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column('services', sa.Column('version', sa.Integer(), nullable=True))
    op.create_index(
        op.f('ix_services_created_by_id'), 'services', ['created_by_id'], unique=False
    )
    op.create_foreign_key(
        'fk_services_created_by_id', 'services', 'users', ['created_by_id'], ['id']
    )

    op.get_bind()
    op.execute(
        'UPDATE services SET created_by_id = (SELECT user_id FROM user_to_service WHERE services.id = user_to_service.service_id LIMIT 1)'
    )
    op.execute('UPDATE services SET version = 1')
    op.execute('INSERT INTO services_history SELECT * FROM services')

    op.alter_column('services', 'created_by_id', nullable=False)
    op.alter_column('services', 'version', nullable=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_services_created_by_id', 'services', type_='foreignkey')
    op.drop_index(op.f('ix_services_created_by_id'), table_name='services')
    op.drop_column('services', 'version')
    op.drop_column('services', 'created_by_id')
    op.drop_index(
        op.f('ix_services_history_created_by_id'), table_name='services_history'
    )
    op.drop_table('services_history')
    ### end Alembic commands ###
