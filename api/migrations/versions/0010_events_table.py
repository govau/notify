"""empty message

Revision ID: 0010_events_table
Revises: 0009_created_by_for_jobs
Create Date: 2016-04-26 13:08:42.892813

"""

# revision identifiers, used by Alembic.
revision = '0010_events_table'
down_revision = '0009_created_by_for_jobs'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('events',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('event_type', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('data', postgresql.JSON(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('events')
    ### end Alembic commands ###
