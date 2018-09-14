"""

Revision ID: 0189_rename_notify_service
Revises: 0188_change_templates_to_dta
Create Date: 2018-07-11 13:37:13.496526

"""
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '0189_rename_notify_service'
down_revision = '0188_change_templates_to_dta'

service_id = 'd6aa2c68-a2d9-4437-ab19-3ae8eb202553'


def upgrade():
    op.execute(
        "update services set name = 'Notify system' where id = '{}'".format(service_id)
    )


def downgrade():
    op.execute(
        "update services set name = 'GOV.UK Notify' where id = '{}'".format(service_id)
    )
