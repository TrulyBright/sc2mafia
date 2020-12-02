import sqlalchemy as sa

metadata = sa.MetaData()

users = sa.Table(
  'users', metadata,
  sa.Column('id', sa.Integer, primary_key=True),
  sa.Column('username', sa.String),
  sa.Column('password', sa.String),
  sa.Column('nickname', sa.String),
  sa.Column('is_superuser', sa.Boolean, nullable=False, default=False),
  sa.Column('disabled', sa.Boolean, nullable=False, default=False)
)
