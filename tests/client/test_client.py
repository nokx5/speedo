import pytest
from speedo_client import SpeedoClient, SpeedoError
from speedo_client.mock_client import MockSpeedoClient


def test_mock_client(make_submission_dict):
    submi_dict = make_submission_dict("test_mock_client", nb_tags=1)
    prac: SpeedoClient = MockSpeedoClient(hostname="mock_it_up!")

    dd = prac.post_submission(submi_dict)
    assert dd.dict() == {"status": "done"}

    dd = prac.get_projects()
    assert submi_dict["project"] in [u["name"] for u in dd.dict()["projects"]]

    dd = prac.get_submission(submi_dict["uid"])
    assert submi_dict["uid"] == dd.dict()["submission"]["uid"]

    dd = prac.get_submissions(user=submi_dict["user"])
    assert submi_dict["uid"] in [sub["uid"] for sub in dd.dict()["submissions"]]

    dd = prac.get_tags()
    assert submi_dict["tags"][0] in [u["name"] for u in dd.dict()["tags"]]

    dd = prac.get_users()
    assert submi_dict["user"] in [u["name"] for u in dd.dict()["users"]]

    with pytest.raises(SpeedoError) as err:
        prac.delete_bind_tag("wrong_uid", "wrong_tag")
    assert "Speedo Server Error." in str(err)

    with pytest.raises(SpeedoError) as err:
        prac.delete_bind_tags("wrong_uid")
    assert "Speedo Server Error." in str(err)

    with pytest.raises(SpeedoError) as err:
        prac.delete_project("wrong_project")
    assert "Speedo Server Error." in str(err)

    with pytest.raises(SpeedoError) as err:
        prac.delete_submission("dummy_submissions")
    assert "Speedo Server Error." in str(err)

    with pytest.raises(SpeedoError) as err:
        prac.delete_tag("wrong_tag")
    assert "Speedo Server Error." in str(err)

    with pytest.raises(SpeedoError) as err:
        prac.delete_user("wrong_user")
    assert "Speedo Server Error." in str(err)

    # keep this test at the end
    dd = prac.post_bind_tags(submi_dict["uid"], ["DUMMY_TAG0"])
    assert dd.dict() == {"status": "done"}
