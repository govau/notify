"""

Revision ID: 0200
Revises: 0199
Create Date: 2018-09-14 08:54:06.235436

"""
from alembic import op
import sqlalchemy as sa


revision = '0200'
down_revision = '0199'


def upgrade():
    op.get_bind()
    op.execute("UPDATE rates SET valid_from = '2017-06-30 14:00:00' WHERE valid_from = '2017-03-31 23:00:00'")


def downgrade():
    op.get_bind()
    op.execute("UPDATE rates SET valid_from = '2017-03-31 23:00:00' WHERE valid_from = '2017-06-30 14:00:00'")
