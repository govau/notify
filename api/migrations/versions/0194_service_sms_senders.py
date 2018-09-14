"""

Revision ID: 0194_service_sms_senders
Revises: 0193_add_provider_details_hist
Create Date: 2018-07-12 14:38:03.091574

"""
from alembic import op
from sqlalchemy.dialects import postgresql

revision = '0194_service_sms_senders'
down_revision = '0193_add_provider_details_hist'

service_sms_sender_id = "286d6176-adbe-7ea7-ba26-b7606ee5e2a4"


def upgrade():
    op.execute(
        """
        UPDATE service_sms_senders
        SET sms_sender = 'GOVAU' where id = '{}'
        """.format(
            service_sms_sender_id
        )
    )


def downgrade():
    op.execute(
        """
        UPDATE service_sms_senders
        SET sms_sender = 'GOVUK' where id = '{}'
        """.format(
            service_sms_sender_id
        )
    )
