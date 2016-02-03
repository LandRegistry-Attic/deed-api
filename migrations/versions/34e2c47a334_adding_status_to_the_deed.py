# flake8: noqa
"""adding status to the deed

Revision ID: 34e2c47a334
Revises: 2ef609ed309
Create Date: 2016-02-03 11:08:54.380809

"""

# revision identifiers, used by Alembic.
revision = '34e2c47a334'
down_revision = '2ef609ed309'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('deed', sa.Column('status', sa.String(length=16), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('deed', 'status')
    ### end Alembic commands ###
