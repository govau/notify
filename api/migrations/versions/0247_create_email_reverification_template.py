"""

Revision ID: 0247
Revises: 0246
Create Date: 2020-06-02 11:16:02.760509

"""
from alembic import op
from datetime import datetime

revision = '0247'
down_revision = '0246'


template_id = '12345678-abcd-abcd-abcd-000000000001'

content = """Hi ((name)),

To complete your email verification for Notify, please click the link below:

((url))
"""


def upgrade():

    generic_insert_statement = """
            INSERT INTO {table}
            VALUES ('{template_id}',
                    'Reverify email address',
                    'email',
                    '{created_at}',
                    null,
                    '{content}',
                    'd6aa2c68-a2d9-4437-ab19-3ae8eb202553',
                    'Verify your email address',
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
