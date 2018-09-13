"""

Revision ID: 0199
Revises: 0198
Create Date: 2018-09-10 09:34:40.184871

"""
from alembic import op
import sqlalchemy as sa


revision = '0199'
down_revision = '0198'

def make_provider_details_upgrade_sql(identifier, priority, supports_international, active):
    return """
        UPDATE provider_details
        SET priority={1}, supports_international={2}, active={3}, updated_at=now(), version=(
            SELECT version from provider_details WHERE identifier = '{0}'
        ) + 1
        WHERE identifier='{0}'
    """.format(
        identifier,
        priority,
        supports_international,
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
        WHERE identifier = {0} AND version = (SELECT version from provider_details WHERE identifier = '{0}')
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
        WHERE identifier = '{0}'
    """.format(identifier)

def upgrade():
    op.execute(make_provider_details_upgrade_sql(identifier="twilio", priority=10, supports_international=True, active=True))
    op.execute(make_provider_details_history_upgrade_sql(identifier="twilio"))

    op.execute(make_provider_details_upgrade_sql(identifier="telstra", priority=15, supports_international=False, active=True))
    op.execute(make_provider_details_history_upgrade_sql(identifier="telstra"))

    op.execute(make_provider_details_upgrade_sql(identifier="mmg", priority=20, supports_international=False, active=False))
    op.execute(make_provider_details_history_upgrade_sql(identifier="mmg"))

    op.execute(make_provider_details_upgrade_sql(identifier="firetext", priority=20, supports_international=False, active=False))
    op.execute(make_provider_details_history_upgrade_sql(identifier="firetext"))

def downgrade():
    op.execute(make_provider_details_history_downgrade_sql(identifier="firetext"))
    op.execute(make_provider_details_downgrade_sql(identifier="firetext"))

    op.execute(make_provider_details_history_downgrade_sql(identifier="mmg"))
    op.execute(make_provider_details_downgrade_sql(identifier="mmg"))

    op.execute(make_provider_details_history_downgrade_sql(identifier="telstra"))
    op.execute(make_provider_details_downgrade_sql(identifier="telstra"))

    op.execute(make_provider_details_history_downgrade_sql(identifier="twilio"))
    op.execute(make_provider_details_downgrade_sql(identifier="twilio"))

