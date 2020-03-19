"""

Revision ID: 0237
Revises: 0236
Create Date: 2020-03-18 22:13:57.400373

"""
import uuid

from alembic import op
import sqlalchemy as sa


revision = '0237'
down_revision = '0236'


def upgrade():
    op.get_bind()
    op.execute("UPDATE provider_rates SET rate = 6.0 WHERE provider_id = (SELECT id FROM provider_details WHERE identifier = 'telstra')")
    op.execute("UPDATE provider_rates SET rate = 6.0 WHERE provider_id = (SELECT id FROM provider_details WHERE identifier = 'twilio')")
    op.execute("UPDATE rates SET rate = 0.06 WHERE valid_from = '2017-06-30 14:00:00'")
    op.execute("UPDATE rates SET rate = 0.06 WHERE valid_from = '2016-05-18 00:00:00'")


def downgrade():
    op.get_bind()
    op.execute("UPDATE rates SET rate = 0.0165 WHERE valid_from = '2016-05-18 00:00:00'")
    op.execute("UPDATE rates SET rate = 0.0158 WHERE valid_from = '2017-06-30 14:00:00'")
    op.execute("UPDATE provider_rates SET rate = 1.8 WHERE provider_id = (SELECT id FROM provider_details WHERE identifier = 'twilio')")
    op.execute("UPDATE provider_rates SET rate = 1.8 WHERE provider_id = (SELECT id FROM provider_details WHERE identifier = 'telstra')")
    
    
