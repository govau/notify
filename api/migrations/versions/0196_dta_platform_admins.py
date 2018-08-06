"""

Revision ID: 0196
Revises: 0195_delete_ses
Create Date: 2018-08-06 15:34:23.126474

"""
from alembic import op
import sqlalchemy as sa


revision = '0196'
down_revision = '0195_delete_ses'

user_ids = [
    '6517d0a3-8299-4272-a75e-8b296805946c',
    '19e3a347-1c1a-45bf-bd44-8cb4903c8307',
]

def upgrade():
    for user_id in user_ids:
        op.execute("""
        UPDATE users SET
              platform_admin = true
        WHERE id = '{user_id}'
        """.format(user_id=user_id)
        )

def downgrade():
    for user_id in user_ids:
        op.execute("""
        UPDATE users SET
              platform_admin = false
        WHERE id = '{user_id}'
        """.format(user_id=user_id)
        )
