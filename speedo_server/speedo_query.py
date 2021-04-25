from typing import List


from speedo_common import api_schemas as api
from .database.deletion import delete_single_submission_tag, delete_bind_submission_tags

from .database.deletion import delete_submission
from .database.selection import (
    select_submission,
    select_submissions,
    select_raw_tags,
    select_users,
    select_projects,
    select_tags,
)
from .database.deletion import delete_user, delete_project, delete_tag

from .database.insertion import submission_bind_tags as bind_submission_tags

from .database.insertion import insert_submission as post_create_submission


def delete_submissions(conn, list_submission_uid):
    for uid in list_submission_uid:
        delete_submission(conn, uid=uid)


def get_list_tag_name(conn, submission_uid: str) -> List[str]:
    return select_raw_tags(conn, submission_uid)


def get_submission(conn, submission_uid: str) -> api.GetSubmission:
    raw_submission = select_submission(conn, submission_uid)
    raw_submission["tags"] = get_list_tag_name(conn, submission_uid)
    raw_submission["timestamp"] = round(
        raw_submission.pop("raw_timestamp").timestamp() * 1000
    )
    return api.GetSubmission(**raw_submission)


def get_submissions(conn, **kwargs) -> List[api.GetSubmission]:
    submissions = []
    for raw in select_submissions(conn, **kwargs):
        raw["tags"] = get_list_tag_name(conn, raw["uid"])
        raw["timestamp"] = round(raw.pop("raw_timestamp").timestamp() * 1000)
        submissions.append(api.GetSubmission(**raw))
    return submissions
