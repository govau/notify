"""

Revision ID: 0208
Revises: 0207
Create Date: 2018-12-07 11:16:02.760509

"""
from alembic import op
from datetime import datetime

revision = '0208'
down_revision = '0207'


template_id = '73a85db3-d017-4bb3-ba2c-2eb36837f234'

content = """Hi Notify Support,

The following user has consented to being contacted for research purposes:

Name: ((name)) 
Email: ((email_address))
Phone: ((phone_number))
"""


def upgrade():

    generic_insert_statement = """
            INSERT INTO {table}
            VALUES ('{template_id}',
                    'User consent to research', 
                    'email',
                    '{created_at}', 
                    null,
                    '{content}',
                    'd6aa2c68-a2d9-4437-ab19-3ae8eb202553',
                    'User consent to research',
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
