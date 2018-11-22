"""

Revision ID: 0206
Revises: 0205
Create Date: 2018-11-22 15:52:14.545537

"""
from alembic import op

revision = '0206'
down_revision = '0205'


def upgrade():
    op.alter_column('ft_billing', 'bst_date', new_column_name='aet_date')


def downgrade():
    op.alter_column('ft_billing', 'aet_date', new_column_name='bst_date')
