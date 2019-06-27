"""

Revision ID: 0222
Revises: 0221
Create Date: 2019-06-27 10:21:14.484343

"""
from alembic import op
import sqlalchemy as sa


revision = '0222'
down_revision = '0221'


def upgrade():
    op.execute("INSERT INTO branding_type (name) VALUES ('notify')")
    op.execute("UPDATE services SET branding = 'notify' WHERE branding = 'govau'")
    op.execute("DELETE FROM branding_type WHERE name = 'govau'")
    op.execute("UPDATE service_sms_senders SET sms_sender = 'Notify' where sms_sender = 'GOVAU'")

def downgrade():
    op.execute("INSERT INTO branding_type (name) VALUES ('govau')")
    op.execute("UPDATE services SET branding = 'govau' WHERE branding = 'notify'")
    op.execute("DELETE FROM branding_type WHERE name = 'notify'")
    op.execute("UPDATE service_sms_senders SET sms_sender = 'GOVAU' where sms_sender = 'Notify'")
