
"""

Revision ID: 0200
Revises: 0199
Create Date: 2018-09-10 09:34:40.184871

"""
from alembic import op
import sqlalchemy as sa


revision = '0199'
down_revision = '0198'

def upgrade():
    op.execute("""
            UPDATE users
            SET platform_admin = true
            WHERE email_address = andrew.oh@digital.gov.au
            """)
    

def downgrade():
    op.execute()

