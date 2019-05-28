"""

Revision ID: 0212
Revises: 0211
Create Date: 2019-05-24 13:44:26.182227

"""
from alembic import op
import sqlalchemy as sa


revision = '0212'
down_revision = '0211'


def upgrade():
    op.add_column('services', sa.Column('count_as_live', sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column('services_history', sa.Column('count_as_live', sa.Boolean(), nullable=False, server_default=sa.true()))

    op.execute("""
        UPDATE
            services
        SET
            count_as_live = not users.platform_admin
        FROM
            users, services_history
        WHERE
            services_history.id = services.id and
            services_history.version = 1 and
            services_history.created_by_id = users.id
        ;
    """)


def downgrade():
    op.drop_column('services_history', 'count_as_live')
    op.drop_column('services', 'count_as_live')
