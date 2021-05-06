from sqlalchemy import Table
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import literal, exists, select, and_

from speedo_server.database.exceptions import EnumError, SpeedoServerError
from .tables import Project, Submission, Tag, TagRelation, User
from .selection import select_simple

from ..session import IS_POSTGRESQL


def insert_simple(conn, target_table: Table, weak=False, **kwargs):
    if weak:
        # insert only if id does not exist
        # inspired by https://stackoverflow.com/a/18605162
        sel = select([literal(v) for v in kwargs.values()]).where(
            ~exists([getattr(target_table.c, key) for key in kwargs.keys()]).where(
                and_(
                    *[
                        getattr(target_table.c, key) == value
                        for key, value in kwargs.items()
                    ]
                )
            )
        )
        ins = target_table.insert().from_select(kwargs.keys(), sel)
    else:
        ins = target_table.insert()
    if IS_POSTGRESQL:
        cmd = ins.returning(target_table.c.id)
    else:
        cmd = ins
    try:
        res = conn.execute(cmd, kwargs)
    except IntegrityError as err:
        raise SpeedoServerError(
            err=err,
            reason=EnumError.InsertionError,
            target_table=target_table,
            **kwargs,
        )
    if weak:  # can not fail
        return select_simple(conn, target_table, **kwargs)[0]
    else:
        if IS_POSTGRESQL:
            return next(res)[0]
        else:
            return res.lastrowid


def insert_user(conn, name):
    return insert_simple(conn, User, name=name)


def insert_project(conn, name):
    return insert_simple(conn, Project, name=name)


def insert_tag(conn, name):
    return insert_simple(conn, Tag, name=name)


def insert_submission(conn, dd):
    """
    1) User (create or get)
    2) Project (create or get)
    4) Submission (create or fail)
    5) Tag (create or get)
    6) TagRelation (create or pass)
    """
    user_id = insert_simple(conn, User, name=dd["user"], weak=True)
    project_id = insert_simple(conn, Project, name=dd["project"], weak=True)
    try:
        submission_id = insert_simple(
            conn,
            Submission,
            user_id=user_id,
            uid=dd["uid"],
            project_id=project_id,
            configuration=dd["configuration"],
            message=dd["message"],
        )
    except IntegrityError as err:
        raise SpeedoServerError(
            err=err, reason=EnumError.InsertionError, target_table=Submission, **dd
        )

    for tag_name in dd["tags"]:
        tag_id = insert_simple(conn, Tag, name=tag_name, weak=True)
        insert_simple(
            conn=conn,
            target_table=TagRelation,
            tag_id=tag_id,
            submission_id=submission_id,
        )


def submission_bind_tags(conn, uid, tags):
    res = select_simple(conn, Submission, uid=uid)
    if res is None:
        raise SpeedoServerError(
            err=LookupError("Submission was not found!"),
            reason=EnumError.SelectionError,
            target_table=Submission,
            submission_uid=uid,
        )
    submission_id = res[0]

    for tag_name in tags:
        tag_id = insert_simple(conn, Tag, name=tag_name, weak=True)
        insert_simple(
            conn=conn,
            target_table=TagRelation,
            submission_id=submission_id,
            tag_id=tag_id,
        )
