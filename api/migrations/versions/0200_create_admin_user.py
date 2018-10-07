"""

Revision ID: 0200
Revises: 0199
Create Date: 2018-09-25 11:36:39.037673

"""
from alembic import op
import os
from datetime import datetime
from app.encryption import hashpw
import uuid


revision = '0200'
down_revision = '0199'
admin_user_id = '7af777d0-2915-4e52-83a3-3690455a5fe7'


def upgrade():
    try:
        os.environ['CREATE_ADMIN_USER']
    except:
        print('CREATE_ADMIN_USER environment variable not found')
        return

    if os.environ['CREATE_ADMIN_USER'].lower() == 'true':
        print('Attempting to create notify-dev@digital.gov.au user...')
        insert_user = """INSERT INTO users (id, name, email_address, created_at, password_changed_at, failed_login_count, _password, mobile_number, state, platform_admin, auth_type)
                         VALUES ('{}', 'Notify Admin', 'notify-dev@digital.gov.au', '{}', '{}', 0,'{}', '+61408184363', 'active', True, 'sms_auth')
                      """
        op.execute(insert_user.format(admin_user_id, datetime.utcnow(), datetime.utcnow(), hashpw(str(uuid.uuid4()))))
        print('Successfully created notify-dev@digital.gov.au user')


def downgrade():
    op.execute("DELETE FROM users WHERE id = '{}'".format(admin_user_id))
