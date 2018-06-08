"""Add nyt into the label table

Revision ID: c3ba36e57a09
Revises: 0ab75264a276
Create Date: 2018-06-06 10:24:50.006292

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3ba36e57a09'
down_revision = '0ab75264a276'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("INSERT INTO label (name) VALUES('New York Times');")


def downgrade():
    op.execute("DELETE FROM label WHERE name='New York Times'")
