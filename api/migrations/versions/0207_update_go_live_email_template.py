"""

Revision ID: 0207
Revises: 0206
Create Date: 2018-12-03 13:19:24.945466

"""
from alembic import op

revision = '0207'
down_revision = '0206'


templates = [{
    'id': "831139ba-a984-11e8-814c-80e6501bb488",
    'new_content': """Hi Notify Support,

The following service has requested to go live: 

Name: ((service_name)) 
URL: ((service_url))
Requested by: ((requested_by))

Organisation type: ((organisation_type))
Agreement signed: ((agreement_signed))
Channel: ((channel))
Start date: ((start_date))
Start volume: ((start_volume))
Peak volume: ((peak_volume))
Features: ((features))
""",
    'old_content': """Hi Notify Support,

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
