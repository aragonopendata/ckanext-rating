"""Create table for Rating model

Revision ID: 015077061c30
Revises: 
Create Date: 2024-05-09 10:04:00.217793

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '015077061c30'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('review',
                    sa.Column('id', sa.String(), nullable=False),
                    sa.Column('package_id', sa.String(), nullable=True),
                    sa.Column('rating', sa.Float(), nullable=False),
                    sa.Column('user_id', sa.String(), nullable=True),
                    sa.Column('rater_ip', sa.String(), nullable=True),
                    sa.Column('created', sa.DateTime(), nullable=True),
                    sa.Column('updated', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('review')
