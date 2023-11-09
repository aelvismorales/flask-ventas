"""Change Producto Imagen ON DELETE

Revision ID: 65130e995b2a
Revises: 92ab2e3a81f1
Create Date: 2023-11-04 18:07:46.626249

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65130e995b2a'
down_revision = '92ab2e3a81f1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.drop_constraint('FK_tipo_producto', type_='foreignkey')
        batch_op.create_foreign_key('FK_tipo_producto', 'tipos', ['tipo_id'], ['id'], ondelete='SET DEFAULT')

    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_constraint('fk_Role', type_='foreignkey')
        batch_op.create_foreign_key('fk_Role', 'roles', ['role_id'], ['id'], ondelete='SET DEFAULT')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_constraint('fk_Role', type_='foreignkey')
        batch_op.create_foreign_key('fk_Role', 'roles', ['role_id'], ['id'])

    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.drop_constraint('FK_tipo_producto', type_='foreignkey')
        batch_op.create_foreign_key('FK_tipo_producto', 'tipos', ['tipo_id'], ['id'])

    # ### end Alembic commands ###