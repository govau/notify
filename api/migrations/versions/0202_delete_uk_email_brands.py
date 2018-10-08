"""

Revision ID: 0202
Revises: 0201
Create Date: 2018-10-08 14:14:48.250456

"""
from alembic import op
import sqlalchemy as sa


revision = '0202'
down_revision = '0201'

VISA_IMMI_ID = '9d25d02d-2915-4e98-874b-974e123e8536'
DATA_GOV_UK_ID = '123496d4-44cb-4324-8e0a-4187101f4bdc'
TFL_DAR_ID = '1d70f564-919b-4c68-8bdf-b8520d92516e'
ENTERPRISE_EUROPE_NETWORK_ID = '89ce468b-fb29-4d5d-bd3f-d468fb6f7c36'


def upgrade():
    op.execute("""
        DELETE FROM email_branding WHERE "id" IN ('{}', '{}', '{}', '{}')
    """.format(VISA_IMMI_ID, DATA_GOV_UK_ID, TFL_DAR_ID, ENTERPRISE_EUROPE_NETWORK_ID))


def downgrade():
    op.execute("""INSERT INTO email_branding VALUES (
        '{}',
        '#9325b2',
        'ho_crest_27px_x2.png',
        'UK Visas & Immigration'
    )""".format(VISA_IMMI_ID))
    op.execute("""INSERT INTO email_branding VALUES (
        '{}',
        '',
        'data_gov_uk_x2.png',
        ''
    )""".format(DATA_GOV_UK_ID))
    op.execute("""INSERT INTO email_branding VALUES (
        '{}',
        '',
        'tfl_dar_x2.png',
        ''
    )""".format(TFL_DAR_ID))
    op.execute("""INSERT INTO email_branding VALUES (
        '{}',
        '',
        'een_x2.png',
        ''
    )""".format(ENTERPRISE_EUROPE_NETWORK_ID))
