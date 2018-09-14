"""

Revision ID: 0192_change_email_from
Revises: 0191_add_provider_details
Create Date: 2018-07-11 16:22:48.916986

"""
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '0192_change_email_from'
down_revision = '0191_add_provider_details'

service_id = 'd6aa2c68-a2d9-4437-ab19-3ae8eb202553'


def upgrade():
    op.execute(
        "update services set email_from = 'gov.au.notify' where id = '{}'".format(
            service_id
        )
    )
    op.execute(
        "update services_history set name = 'Notify system', email_from = 'gov.au.notify' where id = '{}'".format(
            service_id
        )
    )


def downgrade():
    op.execute(
        "update services set name = 'gov.uk.notify' where id = '{}'".format(service_id)
    )
    op.execute(
        "update services_history set name = 'GOV.UK Notify', email_from = 'gov.uk.notify' where id = '{}'".format(
            service_id
        )
    )
