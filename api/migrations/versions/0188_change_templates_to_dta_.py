"""

Revision ID: 0188_change_templates_to_dta
Revises: 0187_change_branding_type_to_dta
Create Date: 2018-07-11 10:05:55.938352

"""
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '0188_change_templates_to_dta'
down_revision = '0187_change_branding_type_to_dta'


def upgrade():
    op.execute(
        """
    UPDATE templates
    SET content = REPLACE(content, 'GOV.UK', 'GOV.AU')
    WHERE content like '%GOV.UK%'
    """
    )
    op.execute(
        """
    UPDATE templates
    SET subject = REPLACE(subject, 'GOV.UK', 'GOV.AU')
    WHERE subject like '%GOV.UK%'
    """
    )
    op.execute(
        """
    UPDATE templates_history
    SET content = REPLACE(content, 'GOV.UK', 'GOV.AU')
    WHERE content like '%GOV.UK%'
    """
    )
    op.execute(
        """
    UPDATE templates_history
    SET subject = REPLACE(subject, 'GOV.UK', 'GOV.AU')
    WHERE subject like '%GOV.UK%'
    """
    )


def downgrade():
    op.execute(
        """
    UPDATE templates
    SET content = REPLACE(content, 'GOV.AU', 'GOV.UK')
    WHERE content like '%GOV.AU%'
    """
    )
    op.execute(
        """
    UPDATE templates
    SET subject = REPLACE(subject, 'GOV.AU', 'GOV.UK')
    WHERE subject like '%GOV.AU%'
    """
    )
    op.execute(
        """
    UPDATE templates_history
    SET content = REPLACE(content, 'GOV.AU', 'GOV.UK')
    WHERE content like '%GOV.AU%'
    """
    )
    op.execute(
        """
    UPDATE templates_history
    SET subject = REPLACE(subject, 'GOV.AU', 'GOV.UK')
    WHERE subject like '%GOV.AU%'
    """
    )
