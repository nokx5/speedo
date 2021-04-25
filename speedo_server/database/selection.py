from speedo_server.database.exceptions import EnumError, SpeedoServerError
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.sql import select, desc, and_
from sqlalchemy.sql.functions import func

from .tables import (
    Submission,
    Project,
    User,
    TagRelation,
    Tag,
)


def select_simple(conn, target_table, **kwargs):
    s = select([target_table]).where(
        and_(*[getattr(target_table.c, key) == value for key, value in kwargs.items()])
    )
    res = conn.execute(s)
    if res.rowcount == 0:
        raise SpeedoServerError(
            err=RuntimeError("Nothing Deleted"),
            reason=EnumError.SelectionError,
            target_table=target_table,
            **kwargs,
        )
    return res.fetchone()


def select_raw_tags(conn, uid: str) -> List[str]:
    returned_column = [Tag.c.name]
    joined_table = TagRelation.join(Submission).join(Tag)
    ins = (
        select(returned_column).select_from(joined_table).where(Submission.c.uid == uid)
    )
    res = conn.execute(ins).fetchall()
    if res is None:
        raise LookupError(f"Could not find uid={uid} in Submission")

    return [t[0] for t in res]


def select_submission(conn, uid: str) -> Dict[str, Any]:
    returned_column = [
        Submission.c.id,
        Submission.c.uid,
        Submission.c.timestamp.label("raw_timestamp"),
        Project.c.name.label("project"),
        User.c.name.label("user"),
        Submission.c.configuration,
        Submission.c.message,
    ]
    joined_table = Submission.join(User).join(Project)
    ins = (
        select(returned_column).select_from(joined_table).where(Submission.c.uid == uid)
    )
    res = conn.execute(ins).fetchone()
    if res is None:
        raise LookupError(f"Could not find uid={uid} in Submission")

    return {c.name: value for c, value in zip(returned_column, res)}


def select_submissions(
    conn,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    mints: Optional[int] = None,
    maxts: Optional[int] = None,
    user: Optional[str] = None,
    project: Optional[str] = None,
    uid: Optional[str] = None,
):
    returned_column = [
        Submission.c.uid,
        Submission.c.timestamp.label("raw_timestamp"),
        Project.c.name.label("project"),
        User.c.name.label("user"),
        Submission.c.configuration,
        Submission.c.message,
    ]
    joined_table = Submission.join(User).join(Project)

    sql_conditions = []
    if mints is not None:
        sql_conditions += [
            Submission.c.timestamp
            >= datetime.fromtimestamp(float(mints) / 1000, tz=timezone.utc)
        ]
    if maxts is not None:
        sql_conditions += [
            Submission.c.timestamp
            < datetime.fromtimestamp(float(maxts) / 1000, tz=timezone.utc)
        ]
    if user is not None:
        sql_conditions += [User.c.name == user]
    if project is not None:
        sql_conditions += [Project.c.name == project]
    if uid is not None:
        sql_conditions += [Submission.c.uid.contains(uid)]

    select_statement = (
        select(returned_column)
        .select_from(joined_table)
        .order_by(desc(Submission.c.timestamp))
        .where(and_(*sql_conditions))
    )

    if limit is not None:
        select_statement = select_statement.limit(limit)

    if offset is not None:
        select_statement = select_statement.offset(offset)

    results = conn.execute(select_statement).fetchall()

    return [
        {c.name: value for c, value in zip(returned_column, row)} for row in results
    ]


def select_users(conn):
    joined = User.join(Submission, User.c.id == Submission.c.user_id, isouter=True)
    cmd = (
        select(
            [
                User.c.name.label("name"),
                func.count(Submission.c.uid).label("submissions_count"),
            ]
        )
        .select_from(joined)
        .group_by(User.c.id)
    )
    res = conn.execute(cmd)
    return [{"name": n, "submissions_count": c} for n, c in res.fetchall()]


def select_projects(conn):
    joined = Project.join(
        Submission, Project.c.id == Submission.c.project_id, isouter=True
    )
    cmd = (
        select(
            [
                Project.c.name.label("name"),
                func.count(Submission.c.id).label("submissions_count"),
            ]
        )
        .select_from(joined)
        .group_by(Project.c.id)
    )
    res = conn.execute(cmd)
    return [{"name": n, "submissions_count": c} for n, c in res.fetchall()]


def select_tags(conn):
    joined = Tag.join(TagRelation, Tag.c.id == TagRelation.c.tag_id, isouter=True)
    cmd = (
        select(
            [
                Tag.c.name.label("name"),
                func.count(TagRelation.c.submission_id).label("submissions_count"),
            ]
        )
        .select_from(joined)
        .group_by(Tag.c.id)
    )
    res = conn.execute(cmd)
    return [{"name": n, "submissions_count": c} for n, c in res.fetchall()]
