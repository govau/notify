"""

Revision ID: 0225
Revises: 0224
Create Date: 2019-07-05 14:44:14.288849

"""
from alembic import op


revision = '0225'
down_revision = '0224'

# This is the date the commit was made that incorrectly set the message limit to
# 25,000 when it should have remained at 250,000.
# By using this date in the where clause below, we only update services that
# were created after this commit was made.
# See https://github.com/govau/notify/commit/b29f135dca87aec32daed0a2b41243b6d0bd89be#diff-9ea0fa34caf8fb2b9fbb389ea322bee4L231
commit_date = '2019-02-05T04:26:25Z'


def upgrade():
    op.execute("update services set message_limit = 250000 where message_limit = 25000 and restricted = false and created_at > '{}'".format(commit_date))
    op.execute("update services_history set message_limit = 250000 where message_limit = 25000 and restricted and created_at > '{}'".format(commit_date))


def downgrade():
    op.execute("update services_history set message_limit = 25000 where message_limit = 250000 and restricted = false and created_at > '{}'".format(commit_date))
    op.execute("update services set message_limit = 25000 where message_limit = 250000 and restricted = false and created_at > '{}'".format(commit_date))
