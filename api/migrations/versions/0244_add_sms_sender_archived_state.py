"""

Revision ID: 0244
Revises: 0243
Create Date: 2020-05-29 12:04:49.988157

"""
from alembic import op
import sqlalchemy as sa


revision = '0244'
down_revision = '0243'


def upgrade():

    op.add_column('service_sms_senders', sa.Column('archived', sa.Boolean(), nullable=False, server_default=sa.false()))

def downgrade():

    op.drop_column('service_sms_senders', 'archived')