"""Indexies

Revision ID: dc800678df87
Revises: d02473150b31
Create Date: 2024-05-22 11:51:45.942983

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc800678df87'
down_revision: Union[str, None] = 'd02473150b31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('summary_texts', sa.Column('service_source', sa.Text(), nullable=True))
    op.create_index('ix_summary_texts_id', 'summary_texts', ['id'], unique=False)
    op.create_index('ix_summary_texts_service_source', 'summary_texts', ['service_source'], unique=False)
    op.create_index('ix_summary_texts_user_id', 'summary_texts', ['user_id'], unique=False)
    op.add_column('transcribed_texts', sa.Column('user_id', sa.BigInteger(), nullable=True))
    op.add_column('transcribed_texts', sa.Column('service_source', sa.Text(), nullable=True))
    op.create_index('ix_transcribed_texts_id', 'transcribed_texts', ['id'], unique=False)
    op.create_index('ix_transcribed_texts_service_source', 'transcribed_texts', ['service_source'], unique=False)
    op.create_index('ix_transcribed_texts_user_id', 'transcribed_texts', ['user_id'], unique=False)
    op.drop_column('transcribed_texts', 'initiator_user_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('transcribed_texts', sa.Column('initiator_user_id', sa.BIGINT(), autoincrement=False, nullable=False))
    op.drop_index('ix_transcribed_texts_user_id', table_name='transcribed_texts')
    op.drop_index('ix_transcribed_texts_service_source', table_name='transcribed_texts')
    op.drop_index('ix_transcribed_texts_id', table_name='transcribed_texts')
    op.drop_column('transcribed_texts', 'service_source')
    op.drop_column('transcribed_texts', 'user_id')
    op.drop_index('ix_summary_texts_user_id', table_name='summary_texts')
    op.drop_index('ix_summary_texts_service_source', table_name='summary_texts')
    op.drop_index('ix_summary_texts_id', table_name='summary_texts')
    op.drop_column('summary_texts', 'service_source')
    # ### end Alembic commands ###
