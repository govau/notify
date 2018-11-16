"""

Revision ID: 0205
Revises: 0204
Create Date: 2018-11-12 15:32:20.317286

"""
from alembic import op
import sqlalchemy as sa


revision = '0205'
down_revision = '0204'


templates = [{
    'id': "4f46df42-f795-4cc4-83bb-65ca312f49cc",
    'new_content': """((user_name)) has invited you to collaborate on ((service_name)) using Notify.

Notify makes it easy to keep people updated by helping you send text messages and emails.

Use the following link to create a Notify account:

((url))

This invitation will stop working at midnight tomorrow. This is to keep ((service_name)) secure.
""",
    'old_content': """((user_name)) has invited you to collaborate on ((service_name)) using Notify.


        Notify makes it easy to keep people updated by helping you send text messages and emails.


        Click this link to create a Notify account:
((url))


        This invitation will stop working at midnight tomorrow. This is to keep ((service_name)) secure.
"""
}]

template_update = """
    UPDATE templates
    SET content = '{}'
    WHERE id = '{}'
"""
template_history_update = """
    UPDATE templates_history
    SET content = '{}'
    WHERE id = '{}'
"""

def upgrade():
    for t in templates:
        op.execute(template_update.format(t['new_content'], t['id']))
        op.execute(template_history_update.format(t['new_content'], t['id']))


def downgrade():
    for t in templates:
        op.execute(template_update.format(t['old_content'], t['id']))
        op.execute(template_history_update.format(t['old_content'], t['id']))
