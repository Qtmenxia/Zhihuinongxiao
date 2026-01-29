import sqlalchemy as sa
import alembic.op as op

def upgrade():
    op.create_table(
        'service_deployments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('service_id', sa.String(length=50), nullable=False),
        sa.Column('farmer_id', sa.String(length=50), nullable=False),
        sa.Column('product_name', sa.String(length=200), nullable=False),
        sa.Column('product_category', sa.String(length=100), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('origin', sa.String(length=100)),
        sa.Column('stock', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('certifications', sa.JSON()),
        sa.Column('deployed_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['service_id'], ['mcp_services.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['farmer_id'], ['farmers.id'], ondelete='CASCADE')
    )
