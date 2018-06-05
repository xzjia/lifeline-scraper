"""Create event table

Revision ID: 0ab75264a276
Revises: 1e4b3e20e30d
Create Date: 2018-06-05 16:10:46.488959

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ab75264a276'
down_revision = '1e4b3e20e30d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'event',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('text', sa.Text()),
        sa.Column('link', sa.Text()),
        sa.Column('label_id', sa.Integer, sa.ForeignKey("label.id")),
    )


def downgrade():
    op.drop_table('event')
