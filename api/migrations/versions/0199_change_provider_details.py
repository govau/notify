"""

Revision ID: 0199
Revises: 0198
Create Date: 2018-09-10 09:34:40.184871

"""
from alembic import op
import sqlalchemy as sa


revision = '0199'
down_revision = '0198'


def upgrade():
    op.execute("UPDATE provider_details SET supports_international=True WHERE identifier='twilio'")
    op.execute("UPDATE provider_details_history SET supports_international=True WHERE identifier='twilio'")
    op.execute("UPDATE provider_details SET priority=15 WHERE identifier='telstra'")
    op.execute("UPDATE provider_details_history SET priority=15 WHERE identifier='telstra'")
    op.execute("UPDATE provider_details SET priority=20, active=False WHERE identifier='mmg'")
    op.execute("UPDATE provider_details_history SET priority=20, active=False WHERE identifier='mmg'")
    op.execute("UPDATE provider_details SET priority=20, active=False WHERE identifier='firetext'")
    op.execute("UPDATE provider_details_history SET priority=20, active=False WHERE identifier='firetext'")


def downgrade():
    op.execute("UPDATE provider_details_history SET priority=10, active=True WHERE identifier='firetext'")
    op.execute("UPDATE provider_details SET priority=10, active=True WHERE identifier='firetext'")
    op.execute("UPDATE provider_details_history SET priority=10, active=True WHERE identifier='mmg'")
    op.execute("UPDATE provider_details SET priority=10, active=True WHERE identifier='mmg'")
    op.execute("UPDATE provider_details_history SET priority=10 WHERE identifier='telstra'")
    op.execute("UPDATE provider_details SET priority=10 WHERE identifier='telstra'")
    op.execute("UPDATE provider_details_history SET supports_international=False WHERE identifier='twilio'")
    op.execute("UPDATE provider_details SET supports_international=False WHERE identifier='twilio'")

