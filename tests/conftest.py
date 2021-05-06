import pytest
from uuid import uuid4

from speedo_server.asgi import app  # this line creates the tables in the DB
from speedo_server.session import engine

from fastapi.testclient import TestClient


@pytest.fixture
def conn():
    with engine.begin() as c:
        yield c


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def uuid():
    return uuid4().hex


@pytest.fixture
def make_uuid():
    def _make_uuid(scope=None):
        if scope is None:
            scope = ""
        if len(scope) > 64:
            raise RuntimeError("Keep it simple, use shorter scopes (<=32).")
        return scope.upper() + uuid4().hex

    return _make_uuid


@pytest.fixture
def make_submission_dict(make_uuid):
    def _make_submission_dict(scope=None, nb_tags=0):
        uuid = make_uuid(scope)
        return dict(
            uid=f"{uuid}",
            configuration=f"configuration_{uuid}",
            project=f"project_{uuid}",
            user=f"user_{uuid}",
            message=f"message_{uuid}",
            tags=[f"TAG{i}_{uuid}" for i in range(nb_tags)],
        )

    return _make_submission_dict


@pytest.fixture
def submission_dict(uuid, make_submission_dict):
    return make_submission_dict()
