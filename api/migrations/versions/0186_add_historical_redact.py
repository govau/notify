"""

Revision ID: 0186
Revises: 0185
Create Date: 2018-05-14 17:36:57.501398

"""
from alembic import op
import sqlalchemy as sa
from flask import current_app

revision = '0186'
down_revision = '0185'

def upgrade():
    op.execute(
        """
        INSERT INTO template_redacted
        (
            template_id,
            redact_personalisation,
            updated_at,
            updated_by_id
        )
        SELECT
            templates.id,
            false,
            now(),
            '{notify_user}'
        FROM
            templates
        LEFT JOIN template_redacted on template_redacted.template_id = templates.id
        WHERE template_redacted.template_id IS NULL
        """.format(notify_user=current_app.config['NOTIFY_USER_ID'])
    )


def downgrade():
    pass
