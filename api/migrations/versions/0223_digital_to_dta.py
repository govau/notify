"""

Revision ID: 0223
Revises: 0222
Create Date: 2019-07-04 10:31:09.719966

"""
from alembic import op


revision = '0223'
down_revision = '0222'


def upgrade():
    # Find all users with an email ending in @digital.gov.au (ignore case).
    # Replace the @digital.gov.au part of their email address with @dta.gov.au.
    # However, only do this for users that don't already have an @dta.gov.au
    # user record. The subsequery takes care of this check.
    op.execute("""
    UPDATE users u1
    SET email_address = regexp_replace(u1.email_address,'@digital.gov.au','@dta.gov.au', 'i')
    WHERE u1.email_address ilike '%@digital.gov.au' AND NOT EXISTS (
        SELECT 1
        FROM users u2
        WHERE u2.email_address = regexp_replace(u1.email_address, '@digital.gov.au', '@dta.gov.au', 'i')
    )
    """)


def downgrade():
    # Essentially the reverse of the upgrade function.
    # Find all users with an email ending in @dta.gov.au (ignore case).
    # Replace the @dta.gov.au part of their email address with @digital.gov.au.
    # However, only do this for users that don't already have an @digital.gov.au
    # user record. The subsequery takes care of this check.
    op.execute("""
    UPDATE users u1
    SET email_address = regexp_replace(u1.email_address,'@dta.gov.au','@digital.gov.au', 'i')
    WHERE u1.email_address ilike '%@dta.gov.au' AND NOT EXISTS (
        SELECT 1
        FROM users u2
        WHERE u2.email_address = regexp_replace(u1.email_address, '@dta.gov.au', '@digital.gov.au', 'i')
    )
    """)
