"""empty message

Revision ID: 0032_notification_created_status
Revises: 0031_store_personalisation
Create Date: 2016-06-21 11:29:28.963615

"""

# revision identifiers, used by Alembic.
revision = '0032_notification_created_status'
down_revision = '0031_store_personalisation'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    status_type = sa.Enum('created', 'sending', 'delivered', 'pending', 'failed',
                          'technical-failure', 'temporary-failure', 'permanent-failure',
                          name='notify_status_type')
    status_type.create(op.get_bind())
    op.add_column('notifications', sa.Column('new_status', status_type, nullable=True))
    op.execute('update notifications set new_status = CAST(CAST(status as text) as notify_status_type)')
    op.alter_column('notifications', 'status', new_column_name='old_status')
    op.alter_column('notifications', 'new_status', new_column_name='status')
    op.drop_column('notifications', 'old_status')
    op.get_bind()
    op.execute('DROP TYPE notify_status_types')
    op.alter_column('notifications', 'status', nullable=False)

    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    status_type = sa.Enum('sending', 'delivered', 'pending', 'failed',
                          'technical-failure', 'temporary-failure', 'permanent-failure',
                          name='notify_status_types')
    status_type.create(op.get_bind())
    op.add_column('notifications', sa.Column('old_status', status_type, nullable=True))
    op.execute("update notifications set status = 'sending' where status = 'created'")
    op.execute('update notifications set old_status = CAST(CAST(status as text) as notify_status_types)')
    op.alter_column('notifications', 'status', new_column_name='new_status')
    op.alter_column('notifications', 'old_status', new_column_name='status')
    op.drop_column('notifications', 'new_status')
    op.get_bind()
    op.execute('DROP TYPE notify_status_type')
    op.alter_column('notifications', 'status', nullable=False)
    ### end Alembic commands ###
