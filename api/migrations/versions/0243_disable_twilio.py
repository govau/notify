"""

Revision ID: 0243
Revises: 0242
Create Date: 2020-05-21 03:37:42.600376

"""
from alembic import op
from datetime import datetime
import uuid


revision = '0243'
down_revision = '0242'


def make_provider_details_upgrade_sql(identifier, priority, active):
    return """
        UPDATE provider_details
        SET priority={1}, active={2}, updated_at=now(), version=(
            SELECT version from provider_details WHERE identifier = '{0}'
        ) + 1
        WHERE identifier='{0}'
    """.format(
        identifier,
        priority,
        active,
    )

def make_provider_details_history_upgrade_sql(identifier):
    return """
        INSERT INTO provider_details_history (id, display_name, identifier, priority, notification_type, active, version, updated_at, created_by_id, supports_international)
        SELECT id, display_name, identifier, priority, notification_type, active, version, updated_at, created_by_id, supports_international FROM provider_details WHERE identifier = '{0}'
    """.format(identifier)

def make_provider_details_history_downgrade_sql(identifier):
    return """
        DELETE FROM provider_details_history
        WHERE identifier = '{0}' AND version = (SELECT version from provider_details WHERE identifier = '{0}')
    """.format(identifier)

def make_provider_details_downgrade_sql(identifier):
    return """
        UPDATE provider_details
        SET display_name = h.display_name,
            identifier = h.identifier,
            priority = h.priority,
            notification_type = h.notification_type,
            active = h.active,
            version = h.version,
            updated_at = h.updated_at,
            created_by_id = h.created_by_id,
            supports_international = h.supports_international
        FROM (
            SELECT id, display_name, identifier, priority, notification_type, active, version, updated_at, created_by_id, supports_international
            FROM provider_details_history
            WHERE identifier = '{0}'
            ORDER BY version desc
            LIMIT 1
        ) h
        WHERE provider_details.identifier = '{0}'
    """.format(identifier)

def upgrade():
    op.execute(make_provider_details_upgrade_sql(identifier="twilio", priority=15, active=False))
    op.execute(make_provider_details_history_upgrade_sql(identifier="twilio"))

    op.execute(make_provider_details_upgrade_sql(identifier="telstra", priority=10, active=True))
    op.execute(make_provider_details_history_upgrade_sql(identifier="telstra"))

def downgrade():

    op.execute(make_provider_details_history_downgrade_sql(identifier="telstra"))
    op.execute(make_provider_details_downgrade_sql(identifier="telstra"))

    op.execute(make_provider_details_history_downgrade_sql(identifier="twilio"))
    op.execute(make_provider_details_downgrade_sql(identifier="twilio"))