"""

Revision ID: 0235
Revises: 0234
Create Date: 2019-08-13 12:38:40.690600

"""
from alembic import op
import sqlalchemy as sa


revision = '0235'
down_revision = '0234'


old_sms_sender = 'Notify'
new_sms_sender = 'NotifyGovAu'

def upgrade():
    op.execute(f"UPDATE service_sms_senders SET sms_sender = '{new_sms_sender}' WHERE sms_sender = '{old_sms_sender}'")

def downgrade():
    op.execute(f"UPDATE service_sms_senders SET sms_sender = '{old_sms_sender}' WHERE sms_sender = '{new_sms_sender}'")
