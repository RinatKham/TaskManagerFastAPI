from datetime import datetime

from sqlalchemy import MetaData, Integer, String, TIMESTAMP, ForeignKey, Table, Column, JSON, Boolean

metadata = MetaData()


role = Table(
    "role",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("permissions", JSON)
)


user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, nullable=False),
    Column("email", String, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("role_id", Integer, ForeignKey(role.c.id)),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False),
)


task = Table(
    "task",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("taskname", String, nullable=False),
    Column("description", String, nullable=False),
    Column("create_time", TIMESTAMP, default=datetime.utcnow),
    Column("deadline", TIMESTAMP),
    Column("done", Boolean, default=False),
    Column("user_id", Integer, ForeignKey("user.id")),
)