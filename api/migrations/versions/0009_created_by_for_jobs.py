"""empty message

Revision ID: 0009_created_by_for_jobs
Revises: 0008_archive_template
Create Date: 2016-04-26 14:54:56.852642

"""

# revision identifiers, used by Alembic.
revision = '0009_created_by_for_jobs'
down_revision = '0008_archive_template'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'jobs', sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.create_index(
        op.f('ix_jobs_created_by_id'), 'jobs', ['created_by_id'], unique=False
    )
    op.create_foreign_key(None, 'jobs', 'users', ['created_by_id'], ['id'])
    op.get_bind()
    op.execute(
        'UPDATE jobs SET created_by_id = \
                (SELECT user_id FROM user_to_service WHERE jobs.service_id = user_to_service.service_id LIMIT 1)'
    )
    op.alter_column('jobs', 'created_by_id', nullable=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'jobs', type_='foreignkey')
    op.drop_index(op.f('ix_jobs_created_by_id'), table_name='jobs')
    op.drop_column('jobs', 'created_by_id')
    ### end Alembic commands ###
