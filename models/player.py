import sqlalchemy as sa
from database import metadata

players = sa.Table(
    "players",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String(100), nullable=False, unique=True),
    sa.Column("health", sa.Integer, default=100),
    sa.Column("damage", sa.Integer, default=10),
    sa.Column("critical", sa.Integer, default=5),
    sa.Column("defense", sa.Integer, default=0),
    sa.Column("level", sa.Integer, default=1),
    sa.Column("coins", sa.Integer, default=0),
    sa.Column("weapon_name", sa.String(100), nullable=True),
    sa.Column("armor_name", sa.String(100), nullable=True),
    sa.Column("victories", sa.Integer, default=0),
)
