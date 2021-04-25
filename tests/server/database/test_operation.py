from speedo_server.database.exceptions import SpeedoServerError
import pytest

from speedo_server.database.insertion import insert_simple
from speedo_server.database.deletion import delete_simple

# from speedo_server.database.selection import select_simple

from speedo_server.database.tables import (
    User,
    Project,
    Tag,
)


def insert_get_and_delete(target_table, ids, data):

    from speedo_server.session import engine

    with engine.begin() as conn:
        insert_simple(conn=conn, target_table=target_table, **ids, **data)

    with engine.begin() as conn:
        with pytest.raises(SpeedoServerError) as err:
            insert_simple(conn=conn, target_table=target_table, **ids, **data)

    with engine.begin() as conn:
        delete_simple(conn=conn, target_table=target_table, **ids)

    with engine.begin() as conn:
        with pytest.raises(SpeedoServerError) as err:
            delete_simple(conn=conn, target_table=target_table, **ids)

    # with pytest.raises(LookupError):
    #     with engine.begin() as conn:
    #         res = select_simple(conn=conn, target_table=target_table, **ids).fetchone()
    #         if res is None:
    #             raise LookupError("nothing found")
    #         assert {**ids, **data} == {
    #             c.name: value for c, value in zip(target_table.columns, res)
    #         }

    with engine.begin() as conn:
        insert_simple(conn=conn, target_table=target_table, **ids, **data)


def test_simple_user(make_submission_dict):
    insert_get_and_delete(
        target_table=User,
        ids={"name": make_submission_dict("test_simple_user")["user"]},
        data={},
    )


def test_simple_project(make_submission_dict):
    insert_get_and_delete(
        target_table=Project,
        ids={"name": make_submission_dict("test_simple_project")["project"]},
        data={},
    )


def test_simple_tag(make_submission_dict):
    tag = make_submission_dict("test_simple_tag", nb_tags=2)["tags"][0]
    insert_get_and_delete(
        target_table=Tag, ids={"name": tag}, data={},
    )
