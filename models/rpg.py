import sqlalchemy as sa
from database import metadata

characters = sa.Table(
    "characters",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("user_id", sa.Integer, nullable=False, unique=True),
    sa.Column("name", sa.String(100), nullable=False),
    sa.Column("health", sa.Integer, default=100),
    sa.Column("damage", sa.Integer, default=10),
    sa.Column("defense", sa.Integer, default=0),
    sa.Column("critical", sa.Integer, default=5),
    sa.Column("level", sa.Integer, default=1),
    sa.Column("weapon_name", sa.String(100), nullable=True),
    sa.Column("weapon_damage", sa.Integer, default=0),
    sa.Column("weapon_crit", sa.Integer, default=0),
    sa.Column("armor_name", sa.String(100), nullable=True),
    sa.Column("armor_defense", sa.Integer, default=0),
    sa.Column("is_alive", sa.Boolean, default=True),
)

battles = sa.Table(
    "battles",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("character_id", sa.Integer, sa.ForeignKey("characters.id"), nullable=False),
    sa.Column("enemy_name", sa.String(100), nullable=False),
    sa.Column("enemy_health_start", sa.Integer, nullable=False),
    sa.Column("result", sa.String(20), nullable=True),  # vitoria, derrota, fuga
    sa.Column("rounds", sa.Integer, default=0),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
)

inventory = sa.Table(
    "inventory",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("character_id", sa.Integer, sa.ForeignKey("characters.id"), nullable=False),
    sa.Column("item_name", sa.String(100), nullable=False),
    sa.Column("item_type", sa.String(20), nullable=False),   # weapon, armor, potion
    sa.Column("rarity", sa.String(20), nullable=False),
    sa.Column("value", sa.Integer, default=0),               # damage_bonus / defense_bonus / heal
    sa.Column("extra", sa.Integer, default=0),               # crit_rate para weapons
    sa.Column("equipped", sa.Boolean, default=False),
)
