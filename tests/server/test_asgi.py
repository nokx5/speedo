from speedo_server.database.exceptions import EnumError


def test_asgi_get_users(client):
    response = client.get("/v2/users")
    assert response.ok


def test_asgi_get_projects(client):
    response = client.get("/v2/projects")
    assert response.ok


def test_asgi_get_tags(client):
    response = client.get("/v2/tags")
    assert response.ok


def test_asgi_post_submission(client, make_submission_dict):
    submission_dict = make_submission_dict("asgi_post_submission")
    response = client.post("/v2/submissions", json=submission_dict)

    assert response.ok
    assert response.json().get("status") == "done"

    # expected errors
    expected = client.post("/v2/submissions", json=submission_dict)
    expected_error = EnumError.InsertionError.value

    assert expected.status_code == expected_error.http_status
    assert expected_error.speedo_alert in expected.json().get("detail")


def test_asgi_post_bind_tags(client, make_submission_dict):
    submission_dict = make_submission_dict("asgi_post_bind_tags", nb_tags=3)
    separated_tags = {"tags": submission_dict.pop("tags")}
    submission_dict["tags"] = []

    # create submission
    response = client.post("/v2/submissions", json=submission_dict)

    assert response.ok
    assert response.json().get("status") == "done"

    # bind tags
    url = f"/v2/submissions/{submission_dict['uid']}/tags"
    response = client.post(url, json=separated_tags)

    assert response.ok
    assert response.json().get("status") == "done"

    # return tags
    response = client.get(f"/v2/submissions/{submission_dict['uid']}")

    assert response.ok
    assert response.json().get("submission").get("tags") == separated_tags.get("tags")

    # expected errors
    expected = client.post("/v2/submissions/uid_is_wrong/tags", json=separated_tags)
    expected_error = EnumError.SelectionError.value

    assert expected.status_code == expected_error.http_status
    assert expected_error.speedo_alert in expected.json().get("detail")


def test_asgi_delete_user(client, make_submission_dict):
    expected = client.delete("/v2/users/invalid_user")
    expected_error = EnumError.DeletionError.value

    assert expected.status_code == expected_error.http_status
    assert expected_error.speedo_alert in expected.json().get("detail")

    submission_dict = make_submission_dict("test_asgi_delete_user")
    test_asgi_post_submission(client, lambda x: submission_dict)

    expected = client.delete(f"/v2/users/{submission_dict['user']}")
    expected_error = EnumError.DeletionError.value

    assert expected.status_code == expected_error.http_status
    assert expected_error.speedo_alert in expected.json().get("detail")


def test_asgi_delete_project(client, make_submission_dict):
    expected = client.delete("/v2/projects/invalid_project")
    expected_error = EnumError.DeletionError.value

    assert expected.status_code == expected_error.http_status
    assert expected_error.speedo_alert in expected.json().get("detail")

    submission_dict = make_submission_dict("test_asgi_delete_project")
    test_asgi_post_submission(client, lambda x: submission_dict)

    expected = client.delete(f"/v2/projects/{submission_dict['project']}")
    expected_error = EnumError.DeletionError.value

    assert expected.status_code == expected_error.http_status
    assert expected_error.speedo_alert in expected.json().get("detail")


def test_asgi_delete_tag(client, make_submission_dict):
    expected = client.delete("/v2/tags/invalid_tag")
    expected_error = EnumError.DeletionError.value

    assert expected.status_code == expected_error.http_status
    assert expected_error.speedo_alert in expected.json().get("detail")

    submission_dict = make_submission_dict("test_asgi_delete_tag", nb_tags=2)
    tag_name = submission_dict["tags"][0]
    test_asgi_post_bind_tags(client, lambda x, nb_tags: submission_dict)

    expected = client.delete(f"/v2/tags/{tag_name}")
    expected_error = EnumError.DeletionError.value

    assert expected.status_code == expected_error.http_status
    assert expected_error.speedo_alert in expected.json().get("detail")


def test_asgi_delete_submission(client, make_submission_dict):
    submission_dict = make_submission_dict("asgi_delete_submission")
    test_asgi_post_submission(client, lambda x: submission_dict)

    response = client.delete(f"/v2/submissions/{submission_dict['uid']}")

    assert response.ok
    assert response.json().get("status") == "done"

    expected = client.get(f"/v2/submissions/{submission_dict['uid']}")
    expected_error = EnumError.SelectionError.value

    assert not expected.ok

    expected = client.delete(f"/v2/submissions/{submission_dict['uid']}")
    expected_error = EnumError.DeletionError.value

    assert expected.status_code == expected_error.http_status
    assert expected_error.speedo_alert in expected.json().get("detail")


def test_asgi_delete_submission_tags(client, make_submission_dict):
    submi_dict = make_submission_dict("asgi_del_submission_tags", nb_tags=2)
    test_asgi_post_bind_tags(client, lambda x, nb_tags: submi_dict)

    response = client.delete(f"/v2/submissions/{submi_dict['uid']}/tags")

    assert response.ok
    assert response.json().get("status") == "done"

    response = client.get(f"/v2/submissions/{submi_dict['uid']}")

    assert response.ok
    assert len(response.json()["submission"]["tags"]) == 0

    expected = client.delete(f"/v2/submissions/uid_is_wrong/tags")
    expected_error = EnumError.DeletionError.value

    assert expected.status_code == expected_error.http_status
    assert expected_error.speedo_alert in expected.json().get("detail")


def test_asgi_delete_single_submission_tags(client, make_submission_dict):
    submi_dict = make_submission_dict("del_single_submission_tags", nb_tags=2)
    tag_name_to_del = submi_dict["tags"][1]
    tag_name_to_stay = submi_dict["tags"][0]
    test_asgi_post_bind_tags(client, lambda x, nb_tags: submi_dict)
    uid = submi_dict["uid"]
    response = client.delete(f"/v2/submissions/{uid}/tags/{tag_name_to_del}")

    assert response.ok
    assert response.json().get("status") == "done"

    response = client.get(f"/v2/submissions/{uid}")

    assert response.ok
    assert response.json()["submission"]["tags"] == [tag_name_to_stay]

    expected = client.delete(f"/v2/submissions/uid_is_wrong/tags/tag_is_wrong")
    expected_error = EnumError.DeletionError.value

    assert expected.status_code == expected_error.http_status
    assert expected_error.speedo_alert in expected.json().get("detail")
