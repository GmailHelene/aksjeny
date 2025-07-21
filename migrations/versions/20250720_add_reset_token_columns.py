"""
Alembic migration: Add missing reset_token columns to users table
"""
from alembic import op
import sqlalchemy as sa

revision = '20250720_add_reset_token_columns'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reset_token', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('reset_token_expires', sa.DateTime(), nullable=True))

def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('reset_token_expires')
        batch_op.drop_column('reset_token')
