"""empty message

Revision ID: 2525683b79b9
Revises: 77ee823b9fbb
Create Date: 2018-04-11 08:37:15.470490

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2525683b79b9'
down_revision = '77ee823b9fbb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('social_o_auth',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('site', sa.String(), nullable=True),
    sa.Column('site_uid', sa.String(), nullable=True),
    sa.Column('site_uname', sa.String(), nullable=True),
    sa.Column('unionid', sa.String(), nullable=True),
    sa.Column('open_id', sa.String(), nullable=True),
    sa.Column('access_token', sa.String(), nullable=True),
    sa.Column('refresh_token', sa.String(), nullable=True),
    sa.Column('expire_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('social_o_auth')
    # ### end Alembic commands ###