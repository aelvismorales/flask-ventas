"""refactor Mesa agregando 2 primary key

Revision ID: 1775d240f2b4
Revises: 0e2cf920dae1
Create Date: 2024-01-07 18:40:12.351882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1775d240f2b4'
down_revision = '0e2cf920dae1'
branch_labels = None
depends_on = None


def upgrade():

    # Drop foreign key constraint in nota_pedidos table
    op.execute("ALTER TABLE nota_pedidos DROP FOREIGN KEY nota_pedidos_ibfk_2")

    # Remove auto_increment from id column
    op.execute('ALTER TABLE mesas MODIFY id INT NOT NULL')
    with op.batch_alter_table('mesas',schema=None) as batch_op:
        batch_op.drop_constraint('PK_mesa', type_='primary')
        batch_op.create_primary_key('PK_mesa', ['id','piso','numero_mesa'])
    # Add auto_increment back to id column
    op.execute("ALTER TABLE mesas MODIFY id INT NOT NULL AUTO_INCREMENT")

    # Add foreign key constraint back to nota_pedidos table
    op.execute("ALTER TABLE nota_pedidos ADD CONSTRAINT nota_pedidos_ibfk_2 FOREIGN KEY (mesa_id) REFERENCES mesas(id)")
    # ### end Alembic commands ###


def downgrade():

    # Drop foreign key constraint in nota_pedidos table
    op.execute("ALTER TABLE nota_pedidos DROP FOREIGN KEY nota_pedidos_ibfk_2")

    # Remove auto_increment from id column
    op.execute("ALTER TABLE mesas MODIFY id INT NOT NULL")
    with op.batch_alter_table('mesas',schema=None) as batch_op:
        batch_op.drop_constraint('PK_mesa', type_='primary')
        batch_op.create_primary_key('PK_mesa', ['id'])
    # Add auto_increment back to id column
    op.execute("ALTER TABLE mesas MODIFY id INT NOT NULL AUTO_INCREMENT")

    # Add foreign key constraint back to nota_pedidos table
    op.execute("ALTER TABLE nota_pedidos ADD CONSTRAINT nota_pedidos_ibfk_2 FOREIGN KEY (mesa_id) REFERENCES mesas(id)")
    # ### end Alembic commands ###

