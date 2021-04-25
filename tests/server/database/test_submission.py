from speedo_server.database.insertion import insert_submission
from speedo_server.database.deletion import delete_submission
from speedo_server.session import engine
from speedo_server.speedo_query import get_submission


def test_create_full_submission(make_submission_dict):
    submission_dict = make_submission_dict("full_submission", nb_tags=8)

    with engine.connect() as conn:
        insert_submission(conn, submission_dict)

    with engine.connect() as conn:
        ret = get_submission(conn, submission_dict["uid"])
    ret_test = ret.dict()
    ret_test.pop("timestamp")
    assert ret_test == submission_dict

    with engine.connect() as conn:
        ret = delete_submission(conn, uid=submission_dict["uid"])
