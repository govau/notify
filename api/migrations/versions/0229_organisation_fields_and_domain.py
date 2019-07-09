"""

Revision ID: 0229
Revises: 0228
Create Date: 2019-07-09 19:46:21.988377

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '0229'
down_revision = '0228'


def upgrade():
    op.create_table(
        'domain',
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('organisation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['organisation_id'], ['organisation.id'], ),
        sa.PrimaryKeyConstraint('domain')
    )

    op.add_column('organisation', sa.Column('email_branding_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_organisation_email_branding_id', 'organisation', 'email_branding', ['email_branding_id'], ['id'])

    op.add_column('organisation', sa.Column('letter_branding_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_organisation_letter_branding_id', 'organisation', 'letter_branding', ['letter_branding_id'], ['id'])

    op.add_column('organisation', sa.Column('agreement_signed', sa.Boolean(), nullable=True))
    op.add_column('organisation', sa.Column('agreement_signed_at', sa.DateTime(), nullable=True))
    op.add_column('organisation', sa.Column('agreement_signed_by_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('organisation', sa.Column('agreement_signed_version', sa.Float(), nullable=True))
    op.add_column('organisation', sa.Column('crown', sa.Boolean(), nullable=True))
    op.add_column('organisation', sa.Column('organisation_type', sa.String(length=255), nullable=True))
    op.create_foreign_key('fk_organisation_agreement_user_id', 'organisation', 'users', ['agreement_signed_by_id'], ['id'])

    op.add_column('organisation', sa.Column('request_to_go_live_notes', sa.Text(), nullable=True))

    op.add_column('organisation', sa.Column('agreement_signed_on_behalf_of_email_address', sa.String(length=255), nullable=True))
    op.add_column('organisation', sa.Column('agreement_signed_on_behalf_of_name', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('organisation', 'agreement_signed_on_behalf_of_name')
    op.drop_column('organisation', 'agreement_signed_on_behalf_of_email_address')

    op.drop_column('organisation', 'request_to_go_live_notes')

    op.drop_constraint('fk_organisation_agreement_user_id', 'organisation', type_='foreignkey')
    op.drop_column('organisation', 'organisation_type')
    op.drop_column('organisation', 'crown')
    op.drop_column('organisation', 'agreement_signed_version')
    op.drop_column('organisation', 'agreement_signed_by_id')
    op.drop_column('organisation', 'agreement_signed_at')
    op.drop_column('organisation', 'agreement_signed')

    op.drop_constraint('fk_organisation_email_branding_id', 'organisation', type_='foreignkey')
    op.drop_column('organisation', 'email_branding_id')

    op.drop_constraint('fk_organisation_letter_branding_id', 'organisation', type_='foreignkey')
    op.drop_column('organisation', 'letter_branding_id')

    op.drop_table('domain')
