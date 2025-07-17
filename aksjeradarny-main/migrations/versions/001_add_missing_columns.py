# Create database migration to add missing columns
"""Add missing user columns

Revision ID: add_missing_columns  
Revises: 
Create Date: 2025-01-17

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_missing_columns'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add missing columns that the application expects
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reset_token', sa.String(100), nullable=True))
        batch_op.add_column(sa.Column('reset_token_expires', sa.DateTime(), nullable=True))
        batch_op.create_unique_constraint('uq_users_reset_token', ['reset_token'])

def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('uq_users_reset_token', type_='unique')
        batch_op.drop_column('reset_token_expires')
        batch_op.drop_column('reset_token')