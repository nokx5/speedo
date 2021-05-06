# mypy: ignore-errors
from sqlalchemy import MetaData, Table, Column, ForeignKey, DateTime, String, Integer
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql.functions import now


metadata = MetaData()

User = Table(
    "speedo_user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(64), unique=True, nullable=False),
)

Project = Table(
    "project",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(128), unique=True, nullable=False),
)

Tag = Table(
    "tag",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(256), unique=True, nullable=False),
)

Submission = Table(
    "submission",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("uid", String, unique=True, index=True),
    Column(
        "timestamp",
        DateTime(timezone=True),
        index=True,
        server_default=now(),
        nullable=False,
    ),
    Column("project_id", None, ForeignKey("project.id"), nullable=False),
    Column("user_id", None, ForeignKey("speedo_user.id"), nullable=False),
    Column("configuration", String(256), nullable=True),
    Column("message", String, nullable=False),
    UniqueConstraint("uid", "project_id", "user_id"),
)


TagRelation = Table(
    "relation_tag_submission",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("tag_id", None, ForeignKey("tag.id"), nullable=False, unique=False),
    Column(
        "submission_id", None, ForeignKey("submission.id"), nullable=False, unique=False
    ),
)
