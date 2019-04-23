"""

Revision ID: 0217
Revises: 0216
Create Date: 2019-04-23 15:18:21.772607

"""
from app.dao.provider_details_dao import (
    get_provider_details_by_identifier,
    dao_update_provider_details,
)

revision = '0217'
down_revision = '0216'

identifier = 'smtp'

def upgrade():
    provider = get_provider_details_by_identifier(identifier)
    provider.active = False
    dao_update_provider_details(provider)


def downgrade():
    provider = get_provider_details_by_identifier(identifier)
    provider.active = True
    dao_update_provider_details(provider)
