"""

Revision ID: 0226
Revises: 0225
Create Date: 2019-07-08 09:30:01.856712

"""
from alembic import op
import sqlalchemy as sa


revision = '0226'
down_revision = '0225'


def upgrade():
    op.add_column('email_branding', sa.Column('text', sa.String(length=255), nullable=True))
    op.execute('UPDATE email_branding SET text = name')

    op.add_column('email_branding', sa.Column('brand_type', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_email_branding_brand_type'), 'email_branding', ['brand_type'], unique=False)
    op.create_foreign_key(None, 'email_branding', 'branding_type', ['brand_type'], ['name'])


def downgrade():
    op.drop_constraint('email_branding_brand_type_fkey', 'email_branding', type_='foreignkey')
    op.drop_index(op.f('ix_email_branding_brand_type'), table_name='email_branding')
    op.drop_column('email_branding', 'brand_type')

    op.drop_column('email_branding', 'text')
