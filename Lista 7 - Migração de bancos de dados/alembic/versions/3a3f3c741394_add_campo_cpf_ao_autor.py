"""add campo cpf ao autor

Revision ID: 3a3f3c741394
Revises: 72c7e37d6640
Create Date: 2025-06-06 14:48:40.593225

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a3f3c741394'
down_revision: Union[str, None] = '72c7e37d6640'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('autor') as batch_op:
        batch_op.add_column(sa.Column('cpf', sa.String(), nullable=True))
        batch_op.create_unique_constraint('uq_autor_cpf', ['cpf'])


def downgrade() -> None:
    with op.batch_alter_table('autor') as batch_op:
        batch_op.drop_constraint('uq_autor_cpf', type_='unique')
        batch_op.drop_column('cpf')
