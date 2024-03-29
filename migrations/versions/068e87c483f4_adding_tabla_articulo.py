"""Adding tabla articulo

Revision ID: 068e87c483f4
Revises: c8b93361ea9e
Create Date: 2023-11-09 09:07:18.049335

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '068e87c483f4'
down_revision = 'c8b93361ea9e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.drop_constraint('FK_imagen_producto', type_='foreignkey')
        batch_op.drop_constraint('FK_tipo_producto', type_='foreignkey')
        batch_op.create_foreign_key('FK_imagen_producto', 'imagenes', ['imagen_id'], ['id'], ondelete='SET DEFAULT')
        batch_op.create_foreign_key('FK_tipo_producto', 'tipos', ['tipo_id'], ['id'], ondelete='SET DEFAULT')

    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_constraint('fk_Role', type_='foreignkey')
        batch_op.drop_constraint('FK_imagen_usuario', type_='foreignkey')
        batch_op.create_foreign_key('fk_Role', 'roles', ['role_id'], ['id'], ondelete='SET DEFAULT')
        batch_op.create_foreign_key('FK_imagen_usuario', 'imagenes', ['imagen_id'], ['id'], ondelete='SET DEFAULT')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_constraint('FK_imagen_usuario', type_='foreignkey')
        batch_op.drop_constraint('fk_Role', type_='foreignkey')
        batch_op.create_foreign_key('FK_imagen_usuario', 'imagenes', ['imagen_id'], ['id'])
        batch_op.create_foreign_key('fk_Role', 'roles', ['role_id'], ['id'])

    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.drop_constraint('FK_tipo_producto', type_='foreignkey')
        batch_op.drop_constraint('FK_imagen_producto', type_='foreignkey')
        batch_op.create_foreign_key('FK_tipo_producto', 'tipos', ['tipo_id'], ['id'])
        batch_op.create_foreign_key('FK_imagen_producto', 'imagenes', ['imagen_id'], ['id'])

    # ### end Alembic commands ###
