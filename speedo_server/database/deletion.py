from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.elements import and_
from sqlalchemy.sql.expression import select


from .tables import Submission, TagRelation, User, Project, Tag
from .exceptions import SpeedoServerError, EnumError


def delete_simple(conn, target_table, **kwargs):
    cmd = target_table.delete().where(
        and_(*[getattr(target_table.c, key) == value for key, value in kwargs.items()])
    )
    try:
        res = conn.execute(cmd)
    except IntegrityError as err:
        raise SpeedoServerError(
            err=err,
            reason=EnumError.DeletionError,
            target_table=target_table,
            **kwargs,
        )

    if res.rowcount == 0:
        raise SpeedoServerError(
            err=RuntimeError("Nothing Deleted"),
            reason=EnumError.DeletionError,
            target_table=target_table,
            **kwargs,
        )


def delete_user(conn, name):
    delete_simple(conn, User, name=name)


def delete_project(conn, name):
    delete_simple(conn, Project, name=name)


def delete_tag(conn, name):
    delete_simple(conn, Tag, name=name)


def delete_single_submission_tag(conn, uid, name):
    stmt = select([Submission.c.id]).where(Submission.c.uid == uid)
    stmt_tag = select([Tag.c.id]).where(Tag.c.name == name)
    remove = (
        TagRelation.delete()
        .where(TagRelation.c.submission_id == stmt)
        .where(TagRelation.c.tag_id == stmt_tag)
    )
    res = conn.execute(remove)
    if res.rowcount == 0:
        raise SpeedoServerError(
            err=RuntimeError("Nothing Deleted"),
            reason=EnumError.DeletionError,
            uid=uid,
        )


def delete_bind_submission_tags(conn, uid):
    stmt = select([Submission.c.id]).where(Submission.c.uid == uid)
    remove = TagRelation.delete().where(TagRelation.c.submission_id == stmt)
    res = conn.execute(remove)
    if res.rowcount == 0:
        raise SpeedoServerError(
            err=RuntimeError("Nothing Deleted"),
            reason=EnumError.DeletionError,
            uid=uid,
        )


def delete_submission(conn, uid):
    """We are not following CRUD good practices.

    deletion of submission has the following order
    2) TagRelation
    3) Submission
    # 3) Tag
    # 4) Project
    # 5) User
    """
    try:
        delete_bind_submission_tags(conn, uid)
    except:
        pass
    delete_simple(conn, Submission, uid=uid)
