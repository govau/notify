"""

Revision ID: 0209
Revises: 0208
Create Date: 2019-03-29 15:06:59.663526

"""
from alembic import op
from datetime import datetime

revision = '209'
down_revision = '0208'


template_id = 'c11f3003-8462-4af6-ba80-fd5719f79e21'

content = """Hi Notify Support,

The following user has submitted the following question/feedback:

User: ((user_name)) 
Email: ((user_email))
Type: ((ticket_type))
Message: ((message))
"""


def upgrade():

    generic_insert_statement = """
            INSERT INTO {table}
            VALUES ('{template_id}',
                    'Support question/feedback', 
                    'email',
                    '{created_at}', 
                    null,
                    '{content}',
                    'd6aa2c68-a2d9-4437-ab19-3ae8eb202553',
                    'Support question/feedback',
                    '6af522d0-2915-4e52-83a3-3690455a5fe6',
                    1,
                    false,
                    'normal',
                    null,
                    false)
            """

    op.execute(generic_insert_statement.format(table='templates', template_id=template_id, created_at=datetime.utcnow(), content=content))
    op.execute(generic_insert_statement.format(table='templates_history', template_id=template_id, created_at=datetime.utcnow(), content=content))


def downgrade():
    op.execute("""DELETE from templates WHERE id = '{template_id}'""".format(template_id=template_id))
    op.execute("""DELETE from templates_history WHERE id = '{template_id}'""".format(template_id=template_id))
