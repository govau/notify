"""

Revision ID: 0236
Revises: 0235
Create Date: 2019-09-13 14:31:46.277842

"""
from alembic import op
import sqlalchemy as sa


revision = '0236'
down_revision = '0235'


def upgrade():
    op.alter_column('inbound_numbers', 'number',
                    existing_type=sa.VARCHAR(length=11),
                    type_=sa.String(length=12),
                    existing_nullable=False,
                    existing_server_default=sa.text(u"''::character varying"))
    op.alter_column('service_sms_senders', 'sms_sender',
                    existing_type=sa.VARCHAR(length=11),
                    type_=sa.String(length=12),
                    existing_nullable=False,
                    existing_server_default=sa.text(u"''::character varying"))


def downgrade():
    # Cannot downgrade because we would truncate data.
    pass
