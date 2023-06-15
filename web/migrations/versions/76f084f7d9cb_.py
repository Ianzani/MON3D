"""empty message

Revision ID: 76f084f7d9cb
Revises: a2fb23713870
Create Date: 2023-06-05 18:17:47.363028

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76f084f7d9cb'
down_revision = 'a2fb23713870'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('current', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('current')

    # ### end Alembic commands ###
