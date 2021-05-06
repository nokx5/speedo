import pytest
from datetime import datetime

from speedo_server.session import IS_POSTGRESQL


def test_docs_available(client):
    response = client.get("/docs")

    assert response.ok


def test_submissions(client):
    response = client.get("/v2/submissions")

    assert response.ok

    response = client.get(
        "/v2/submissions",
        params={
            "limit": 1,
            "offset": 0,
            "mints": 0,
            "maxts": 0,
            "user": "test",
            "project": "test",
            "uid": "test",
        },
    )
    assert response.ok


def test_submission_single(client, make_submission_dict):
    send_submission = make_submission_dict()
    submission_uid = send_submission["uid"]

    response = client.get(f"/v2/submissions/{submission_uid}")
    assert response.status_code == 404

    response = client.post("/v2/submissions", json=send_submission)
    assert response.ok

    response = client.get(f"/v2/submissions/{submission_uid}")

    assert response.ok

    returned_submission = response.json()["submission"]

    assert returned_submission.pop("timestamp")

    assert returned_submission == send_submission


def test_submission_single_check(client, make_submission_dict):

    response = client.get("/v2/submissions", params={"limit": 1})

    assert len(response.json()["submissions"]) == 1

    response = client.get("/v2/submissions", params={})

    assert len(response.json()["submissions"]) > 0

    prev_n_submission = len(response.json()["submissions"])

    for i in range(13):
        client.post("/v2/submissions", json=make_submission_dict())

    n_submission = len(client.get("/v2/submissions").json()["submissions"])
    assert n_submission == prev_n_submission + 13


# BASIC OPERATIONS


def test_create_submission(client, submission_dict):
    response = client.post("/v2/submissions", json=submission_dict)

    assert response.ok
    assert response.json().get("status") == "done"


# PARAMETRIZED TESTS ON BASIC OPERATIONS


mark_params_check_status_code = pytest.mark.parametrize(
    "post,code", ((True, 200), (False, 404)), ids=("200", "404")
)


@mark_params_check_status_code
def test_get_submission(client, submission_dict, post, code):
    if post:
        client.post("/v2/submissions", json=submission_dict)

    response = client.get(f"/v2/submissions/{submission_dict['uid']}")

    assert response.status_code == code


@mark_params_check_status_code
def test_delete_submission(client, submission_dict, post, code):
    if post:
        client.post("/v2/submissions", json=submission_dict)
    response = client.delete(f"/v2/submissions/{submission_dict['uid']}")

    assert response.status_code == code


# VALIDATE CONTENT


def test_submission_content(client, submission_dict):
    client.post("/v2/submissions", json=submission_dict)
    submission_uid = submission_dict["uid"]

    response = client.get(f"/v2/submissions/{submission_uid}")

    assert response.json()["submission"].get("uid") == submission_dict.get("uid")


def test_deleted_submission_is_gone(client, submission_dict):
    client.post("/v2/submissions", json=submission_dict)
    client.delete(f"/v2/submissions/{submission_dict['uid']}")

    response = client.get(f"/v2/submissions/{submission_dict['uid']}")

    assert response.status_code == 404


def test_submissions_listing(client, submission_dict):
    client.post("/v2/submissions", json=submission_dict)

    response = client.get(f"/v2/submissions")

    submissions_uids = {sub["uid"] for sub in response.json()["submissions"]}

    assert submission_dict["uid"] in submissions_uids


def test_submissions_with_tags(client, make_submission_dict):
    submission_dict = make_submission_dict()
    submission_dict["tags"] = [submission_dict["uid"] + "_tag_app"]

    client.post("/v2/submissions", json=submission_dict)

    response = client.get(f"/v2/submissions", params=dict(uid=submission_dict["uid"]))

    assert response.json()["submissions"][0]["tags"][0] == submission_dict["tags"][0]


# FILTERS


def test_limit_submissions(client, make_submission_dict):
    num_create = 8
    num_get = 4

    for _ in range(num_create):
        client.post("/v2/submissions", json=make_submission_dict())

    data = client.get("/v2/submissions", params=dict(limit=num_get)).json()

    assert len(data["submissions"]) == num_get


def test_offset_submissions(client, make_submission_dict):
    num_create = 18
    num_get = 4

    for _ in range(num_create):
        client.post("/v2/submissions", json=make_submission_dict())

    all_data = client.get("/v2/submissions", params=dict(limit=num_create)).json()
    first_data = client.get("/v2/submissions", params=dict(limit=num_get)).json()
    next_data = client.get(
        "/v2/submissions", params=dict(limit=num_get, offset=num_get)
    ).json()

    all_uids = {s["uid"] for s in all_data["submissions"]}
    first_uids = {s["uid"] for s in first_data["submissions"]}
    next_uids = {s["uid"] for s in next_data["submissions"]}

    assert all_uids & first_uids == first_uids
    assert all_uids & next_uids == next_uids
    assert first_uids & next_uids == set()


def test_submission_user_filter(client, make_submission_dict):
    target_sub_dict = make_submission_dict()
    target_sub_dict["user"] = "target"

    other_sub_dict = make_submission_dict()

    client.post("/v2/submissions", json=target_sub_dict)
    client.post("/v2/submissions", json=other_sub_dict)

    data = client.get("/v2/submissions", params=dict(user="target")).json()
    users = {s["user"] for s in data["submissions"]}

    assert set(["target"]) == users


def test_submission_project_filter(client, make_submission_dict):
    target_sub_dict = make_submission_dict()
    target_sub_dict["project"] = "target"

    other_sub_dict = make_submission_dict()

    client.post("/v2/submissions", json=target_sub_dict)
    client.post("/v2/submissions", json=other_sub_dict)

    data = client.get("/v2/submissions", params=dict(project="target")).json()
    projects = {s["project"] for s in data["submissions"]}

    assert set(["target"]) == projects


def test_submission_wildcard_uid_filter(client, make_submission_dict):
    target_sub_dict = make_submission_dict()
    target_sub_dict["uid"] = target_sub_dict["uid"] + "_target"

    other_sub_dict = make_submission_dict()

    client.post("/v2/submissions", json=target_sub_dict)
    client.post("/v2/submissions", json=other_sub_dict)

    data = client.get("/v2/submissions", params=dict(uid="target")).json()
    uids = {s["uid"] for s in data["submissions"]}

    assert target_sub_dict["uid"] in uids
