"""create label table

Revision ID: 1e4b3e20e30d
Revises: 
Create Date: 2018-06-05 15:56:10.898746

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e4b3e20e30d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'label',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.Text(), nullable=False),
    )


def downgrade():
    op.drop_table('label')
