"""

Revision ID: 0185
Revises: 0184_alter_primary_key_1
Create Date: 2018-05-14 12:27:41.127488

"""
from alembic import op
import sqlalchemy as sa
import datetime
import uuid

revision = '0185'
down_revision = '0184_alter_primary_key_1'

user_id = '6af522d0-2915-4e52-83a3-3690455a5fe6'
service_id = 'd6aa2c68-a2d9-4437-ab19-3ae8eb202553'

permissions = [
    'manage_users',
    'manage_templates',
    'manage_settings',
    'send_texts',
    'send_emails',
    'send_letters',
    'manage_api_keys',
    'view_activity',
]


def upgrade():
    op.execute(
        """
    UPDATE users SET
          email_address = 'notify-service-user@digital.gov.au'
    WHERE email_address = 'notify-service-user@digital.cabinet-office.gov.uk'
    """
    )

    for permission in permissions:
        op.execute(
            """
        INSERT INTO permissions
               (id, service_id, user_id, permission, created_at)
        VALUES ('{id}', '{service_id}', '{user_id}', '{permission}', '{created_at}')
        """.format(
                id=str(uuid.uuid4()),
                service_id=service_id,
                user_id=user_id,
                permission=permission,
                created_at=datetime.datetime.utcnow(),
            )
        )


def downgrade():
    op.execute(
        """
    UPDATE users SET
          email_address = 'notify-service-user@digital.cabinet-office.gov.uk',
          mobile_number = '+441234123412'
    WHERE email_address = 'notify-service-user@digital.gov.au'
    """
    )

    op.execute(
        """
    DELETE FROM permissions WHERE user_id = '{user_id}'
    """.format(
            user_id=user_id
        )
    )
