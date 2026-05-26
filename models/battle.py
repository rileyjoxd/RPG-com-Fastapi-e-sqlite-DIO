import sqlalchemy as sa
from database import metadata

battles = sa.Table(
    "battles",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("player_id", sa.Integer, sa.ForeignKey("players.id"), nullable=False),
    sa.Column("enemy_name", sa.String(100), nullable=False),
    sa.Column("result", sa.String(20), nullable=False),  # victory, defeat, fled
    sa.Column("damage_dealt", sa.Integer, default=0),
    sa.Column("damage_taken", sa.Integer, default=0),
    sa.Column("loot", sa.String(500), nullable=True),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
)
