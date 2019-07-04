"""

Revision ID: 0223
Revises: 0222
Create Date: 2019-07-04 10:31:09.719966

"""
from alembic import op


revision = '0223'
down_revision = '0222'


def upgrade():
    op.execute("""
    UPDATE users SET
          email_address = 'notify-service-user@dta.gov.au'
    WHERE email_address = 'notify-service-user@digital.gov.au'
    """)

    op.execute("""
    UPDATE users SET
          email_address = 'notify-dev@dta.gov.au'
    WHERE email_address = 'notify-dev@digital.gov.au'
    """)


def downgrade():
    op.execute("""
    UPDATE users SET
          email_address = 'notify-dev@digital.gov.au'
    WHERE email_address = 'notify-dev@dta.gov.au'
    """)

    op.execute("""
    UPDATE users SET
          email_address = 'notify-service-user@digital.gov.au'
    WHERE email_address = 'notify-service-user@dta.gov.au'
    """)
