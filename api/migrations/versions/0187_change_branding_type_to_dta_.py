"""

Revision ID: 0187_change_branding_type_to_dta
Revises: 0186
Create Date: 2018-07-11 08:44:11.695194

"""
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '0187_change_branding_type_to_dta'
down_revision = '0186'


def upgrade():
    op.execute(
        """
    INSERT INTO branding_type(name) VALUES ('govau')
    """
    )
    op.execute(
        """
    UPDATE services SET
          branding = 'govau'
    WHERE branding = 'govuk'
    """
    )
    op.execute(
        """
    DELETE FROM branding_type WHERE name = 'govuk'
    """
    )


def downgrade():
    op.execute(
        """
    INSERT INTO branding_type(name) VALUES ('govuk')
    """
    )
    op.execute(
        """
    UPDATE services SET
          branding = 'govuk'
    WHERE branding = 'govau'
    """
    )
    op.execute(
        """
    DELETE FROM branding_type WHERE name = 'govau'
    """
    )
