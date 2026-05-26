import sqlalchemy as sa
from database import metadata

inventory = sa.Table(
    "inventory",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("player_id", sa.Integer, sa.ForeignKey("players.id"), nullable=False),
    sa.Column("item_name", sa.String(100), nullable=False),
    sa.Column("item_type", sa.String(20), nullable=False),  # weapon, armor, potion
    sa.Column("rarity", sa.String(20), nullable=False),
    sa.Column("damage_bonus", sa.Integer, nullable=True),
    sa.Column("crit_rate", sa.Integer, nullable=True),
    sa.Column("defense_bonus", sa.Integer, nullable=True),
    sa.Column("heal", sa.Integer, nullable=True),
    sa.Column("equipped", sa.Boolean, default=False),
)
