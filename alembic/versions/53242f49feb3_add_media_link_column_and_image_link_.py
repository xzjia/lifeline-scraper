"""Add media_link column and image_link for event table

Revision ID: 53242f49feb3
Revises: 1d019196b47c
Create Date: 2018-06-13 16:50:01.903764

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '53242f49feb3'
down_revision = '1d019196b47c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('event', sa.Column('image_link', sa.TEXT))
    op.add_column('event', sa.Column('media_link', sa.TEXT))


def downgrade():
    op.drop_column('event', 'image_link')
    op.drop_column('event', 'media_link')
