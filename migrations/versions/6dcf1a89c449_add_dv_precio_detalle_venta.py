"""Add dv_precio detalle_Venta

Revision ID: 6dcf1a89c449
Revises: 8072196fcea5
Create Date: 2023-11-16 18:04:04.277417

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6dcf1a89c449'
down_revision = '8072196fcea5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('detalle_venta', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dv_precio', sa.Numeric(precision=10, scale=2), nullable=True))

    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.drop_constraint('FK_tipo_producto', type_='foreignkey')
        batch_op.drop_constraint('FK_imagen_producto', type_='foreignkey')
        batch_op.create_foreign_key('FK_tipo_producto', 'tipos', ['tipo_id'], ['id'], ondelete='SET DEFAULT')
        batch_op.create_foreign_key('FK_imagen_producto', 'imagenes', ['imagen_id'], ['id'], ondelete='SET DEFAULT')

    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_constraint('FK_imagen_usuario', type_='foreignkey')
        batch_op.drop_constraint('fk_Role', type_='foreignkey')
        batch_op.create_foreign_key('FK_imagen_usuario', 'imagenes', ['imagen_id'], ['id'], ondelete='SET DEFAULT')
        batch_op.create_foreign_key('fk_Role', 'roles', ['role_id'], ['id'], ondelete='SET DEFAULT')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_constraint('fk_Role', type_='foreignkey')
        batch_op.drop_constraint('FK_imagen_usuario', type_='foreignkey')
        batch_op.create_foreign_key('fk_Role', 'roles', ['role_id'], ['id'])
        batch_op.create_foreign_key('FK_imagen_usuario', 'imagenes', ['imagen_id'], ['id'])

    with op.batch_alter_table('productos', schema=None) as batch_op:
        batch_op.drop_constraint('FK_imagen_producto', type_='foreignkey')
        batch_op.drop_constraint('FK_tipo_producto', type_='foreignkey')
        batch_op.create_foreign_key('FK_imagen_producto', 'imagenes', ['imagen_id'], ['id'])
        batch_op.create_foreign_key('FK_tipo_producto', 'tipos', ['tipo_id'], ['id'])

    with op.batch_alter_table('detalle_venta', schema=None) as batch_op:
        batch_op.drop_column('dv_precio')

    # ### end Alembic commands ###
