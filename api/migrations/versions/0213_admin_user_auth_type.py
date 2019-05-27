"""

Revision ID: 0213
Revises: 0212
Create Date: 2019-05-27 14:19:16.330511

"""
import os
from alembic import op
import sqlalchemy as sa


revision = '0213'
down_revision = '0212'


def upgrade():
    try:
        os.environ['CREATE_ADMIN_USER']
    except:
        print('CREATE_ADMIN_USER environment variable not found, skipping')
        return

    if os.environ['CREATE_ADMIN_USER'].lower() == 'true':
        op.execute("""
        UPDATE users SET
            auth_type = 'email_auth'
        WHERE email_address = 'notify-dev@digital.gov.au'
        """)


def downgrade():
    pass
