"""

Revision ID: 0236
Revises: 0235
Create Date: 2019-11-26 11:24:31.565916

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0236'
down_revision = '0235'


def upgrade():
    op.create_table('sap_oauth2_clients',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', sa.String(length=48), nullable=False),
        sa.Column('client_secret', sa.String(length=120), nullable=False),
        sa.Column('client_id_issued_at', sa.Integer(), nullable=False, default=0),
        sa.Column('client_secret_expires_at', sa.Integer(), nullable=False, default=0),
        sa.Column('client_metadata', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('client_id')
    )

    op.create_table('sap_oauth2_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('client_id', sa.String(length=48), nullable=False),
        sa.Column('token_type', sa.String(length=40), nullable=False),
        sa.Column('access_token', sa.String(length=255), nullable=False),
        sa.Column('refresh_token', sa.String(length=255), nullable=True),
        sa.Column('scope', sa.Text(), nullable=False, default=''),
        sa.Column('revoked', sa.Boolean(), nullable=False, default=False),
        sa.Column('issued_at', sa.Integer(), nullable=False),
        sa.Column('expires_in', sa.Integer(), nullable=False, default=0),

        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('access_token')
    )
    op.create_index(op.f('ix_sap_oauth2_tokens_refresh_token'), 'sap_oauth2_tokens', ['refresh_token'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_sap_oauth2_tokens_refresh_token'), table_name='sap_oauth2_tokens')
    op.drop_table('sap_oauth2_tokens')
    op.drop_table('sap_oauth2_clients')
