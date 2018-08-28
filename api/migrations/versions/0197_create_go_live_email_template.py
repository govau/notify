"""

Revision ID: 0197
Revises: 0196
Create Date: 2018-08-24 14:31:34.732360

"""
from alembic import op
from datetime import datetime

revision = '0197'
down_revision = '0196'

template_id = '831139ba-a984-11e8-814c-80e6501bb488'

content = """Hi Notify Support,

The following service has requested to go live: 

Name: ((service_name)) 
URL: ((service_url))

Organisation type: ((organisation_type))
Agreement signed: ((agreement_signed))
Channel: ((channel))
Start date: ((start_date))
Start volume: ((start_volume))
Peak volume: ((peak_volume))
Features: ((features))
"""


def upgrade():

    generic_insert_statement = """
            INSERT INTO {table}
            VALUES ('{template_id}',
                    'Request to go live', 
                    'email',
                    '{created_at}', 
                    null,
                    '{content}',
                    'd6aa2c68-a2d9-4437-ab19-3ae8eb202553',
                    'Request to go live - ((service_name))',
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
