"""Add wikipedia label into label table

Revision ID: 812fd2e73486
Revises: 9ae401c6c30c
Create Date: 2018-06-08 15:02:18.313779

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '812fd2e73486'
down_revision = '9ae401c6c30c'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("INSERT INTO label (name) VALUES('Wikipedia');")


def downgrade():
    op.execute("DELETE FROM label WHERE name='Wikipedia'")
