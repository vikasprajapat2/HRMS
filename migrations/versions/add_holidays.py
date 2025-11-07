"""Add holidays table and update attendance

Revision ID: 12345678901234
Create Date: 2025-11-07
"""

revision = '12345678901234'
down_revision = None
branch_labels = None
depends_on = None
from alembic import op
import sqlalchemy as sa
from datetime import date

def upgrade():
    # Create holidays table
    op.create_table(
        'holidays',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('type', sa.String(50)),
        sa.Column('is_paid', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )

    # Add description column to attendance table
    op.add_column('attendances', sa.Column('description', sa.Text()))

    # Insert some default holidays for 2025
    holidays_table = sa.table('holidays',
        sa.column('name', sa.String),
        sa.column('date', sa.Date),
        sa.column('description', sa.Text),
        sa.column('type', sa.String),
        sa.column('is_paid', sa.Boolean)
    )

    default_holidays = [
        ('New Year\'s Day', date(2025, 1, 1), 'New Year celebration', 'government', True),
        ('Republic Day', date(2025, 1, 26), 'National holiday', 'government', True),
        ('Good Friday', date(2025, 4, 18), 'Religious holiday', 'government', True),
        ('Labor Day', date(2025, 5, 1), 'International Workers\' Day', 'government', True),
        ('Independence Day', date(2025, 8, 15), 'National holiday', 'government', True),
        ('Gandhi Jayanti', date(2025, 10, 2), 'National holiday', 'government', True),
        ('Christmas', date(2025, 12, 25), 'Religious holiday', 'government', True),
    ]

    for holiday in default_holidays:
        op.execute(
            holidays_table.insert().values(
                name=holiday[0],
                date=holiday[1],
                description=holiday[2],
                type=holiday[3],
                is_paid=holiday[4]
            )
        )

def downgrade():
    op.drop_column('attendances', 'description')
    op.drop_table('holidays')