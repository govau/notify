"""

Revision ID: 0203
Revises: 0202
Create Date: 2018-11-07 15:27:14.933094

"""
from alembic import op
import sqlalchemy as sa


revision = '0203'
down_revision = '0202'

identifier = 'telstra'

def upgrade():
    op.execute("""
        UPDATE provider_details
        SET active={0}
        WHERE identifier='{1}'
    """.format(
        False,
        identifier,
    ))


def downgrade():
    op.execute("""
        UPDATE provider_details
        SET active={0}
        WHERE identifier='{1}'
    """.format(
        True,
        identifier,
    ))
