import os
from time import time

from fastapi import Depends, FastAPI, HTTPException
from fastapi import Response, Request
from prometheus_client import Counter
from prometheus_client import make_asgi_app


from speedo_common import api_schemas as api
from speedo_common.version import speedo_version

from .session import engine
from . import speedo_query
from .database.exceptions import SpeedoServerError


counter = Counter("speedo_requests_total", "speedo all requests counter")
counter_errors = Counter(
    "speedo_requests_errors_total", "speedo error requests counter",
)
cummulative_request_duration = Counter(
    "speedo_request_duration_seconds_total", "speedo cummulative request duration",
)

app = FastAPI(
    title="Speedo",
    description="Speedo - a fast RESTful web API",
    version=speedo_version,
    # openapi_prefix=os.environ.get("PREFIX", "/kubernetes/speedo-main/"),
)

prometheus_app = make_asgi_app()

app.mount("/metrics", prometheus_app)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    with engine.begin() as conn:
        try:
            request.state.db = conn
            start = time()
            response = await call_next(request)
        except Exception:
            counter_errors.inc()
            raise
        finally:
            if "metrics" not in request.url.path:
                elapsed_time = time() - start
                counter.inc()
                cummulative_request_duration.inc(elapsed_time)

    response.headers["access-control-allow-credentials"] = "true"
    response.headers["access-control-allow-methods"] = "GET,POST,OPTIONS,DELETE"
    response.headers["access-control-allow-origin"] = "*"
    return response


def get_db(request: Request):
    return request.state.db


@app.get("/v2/users", response_model=api.WrapGetUsers)
def get_info_users(db=Depends(get_db)):
    users = speedo_query.select_users(db)
    return api.WrapGetUsers(users=users)


@app.get("/v2/projects", response_model=api.WrapGetProjects)
def get_info_projects(db=Depends(get_db)):
    projects = speedo_query.select_projects(db)
    return api.WrapGetProjects(projects=projects)


@app.get("/v2/tags", response_model=api.WrapGetTags)
def get_info_tags(db=Depends(get_db)):
    tags = speedo_query.select_tags(db)
    return api.WrapGetTags(tags=tags)


@app.get("/v2/submissions", response_model=api.WrapGetSubmissions)
def get_list_submission(
    limit: int = None,
    offset: int = None,
    mints: int = None,
    maxts: int = None,
    user: str = None,
    project: str = None,
    uid: str = None,
    db=Depends(get_db),
):
    list_submission_dict = speedo_query.get_submissions(
        db,
        limit=limit,
        offset=offset,
        mints=mints,
        maxts=maxts,
        user=user,
        project=project,
        uid=uid,
    )
    return api.WrapGetSubmissions(submissions=list_submission_dict)


@app.get("/v2/submissions/{uid}", response_model=api.WrapGetSubmission)
def get_submission(uid: str, db=Depends(get_db)):
    try:
        submission_dict = speedo_query.get_submission(db, uid)
    except LookupError:
        raise HTTPException(404, f"Submission {uid} not found")

    return api.WrapGetSubmission(submission=submission_dict)


@app.post("/v2/submissions", response_model=api.Status)
def create_submission(submission: api.PostSubmission, db=Depends(get_db)):
    try:
        speedo_query.post_create_submission(db, submission.dict())
    except SpeedoServerError as err:
        err.to_http()
    return api.Status(status="done")


@app.post("/v2/submissions/{uid}/tags", response_model=api.Status)
def bind_submission_to_tag(
    uid: str, tags: api.APIBindTags, db=Depends(get_db),
):
    try:
        speedo_query.bind_submission_tags(db, uid=uid, **tags.dict())
    except SpeedoServerError as err:
        err.to_http()
    return api.Status(status="done")


@app.delete("/v2/users/{name}", response_model=api.Status)
def delete_user(name: str, db=Depends(get_db)):
    try:
        speedo_query.delete_user(db, name=name)
    except SpeedoServerError as err:
        err.to_http()
    return api.Status(status="done")


@app.delete("/v2/projects/{name}", response_model=api.Status)
def delete_project(name: str, db=Depends(get_db)):
    try:
        speedo_query.delete_project(db, name=name)
    except SpeedoServerError as err:
        err.to_http()
    return api.Status(status="done")


@app.delete("/v2/tags/{name}", response_model=api.Status)
def delete_tag(name: str, db=Depends(get_db)):
    try:
        speedo_query.delete_tag(db, name=name)
    except SpeedoServerError as err:
        err.to_http()
    return api.Status(status="done")


@app.delete("/v2/submissions/{uid}", response_model=api.Status)
def delete_submission(uid: str, db=Depends(get_db)):
    try:
        speedo_query.delete_submission(db, uid=uid)
    except SpeedoServerError as err:
        err.to_http()
    return api.Status(status="done")


@app.delete("/v2/submissions/{uid}/tags", response_model=api.Status)
def delete_bind_submission_tag(uid: str, db=Depends(get_db)):
    try:
        speedo_query.delete_bind_submission_tags(db, uid=uid)
    except SpeedoServerError as err:
        err.to_http()
    return api.Status(status="done")


@app.delete("/v2/submissions/{uid}/tags/{name}", response_model=api.Status)
def delete_single_bind_submission_tag(uid: str, name: str, db=Depends(get_db)):
    try:
        speedo_query.delete_single_submission_tag(db, uid=uid, name=name)
    except SpeedoServerError as err:
        err.to_http()
    return api.Status(status="done")
