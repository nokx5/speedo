from typing import List, Optional
from pydantic import BaseModel


class DefaultModel(BaseModel):
    # throw an exception if someone sends an unknown field
    # I put it it for testing purposes
    # we can remove it again for the deployment
    class Config:
        extra = "forbid"


class Status(BaseModel):
    status: str


class PostSubmission(BaseModel):
    uid: str
    configuration: str
    project: str
    user: str
    message: str
    tags: List[str]


class GetSubmission(BaseModel):
    uid: str
    configuration: str
    project: str
    user: str
    message: str
    tags: List[str]
    timestamp: int


class APIBindTags(BaseModel):
    tags: List[str]


class GetSimpleInfo(BaseModel):
    name: Optional[str]
    submissions_count: int


class WrapGetUsers(BaseModel):
    users: List[GetSimpleInfo]


class WrapGetProjects(BaseModel):
    projects: List[GetSimpleInfo]


class WrapGetTags(BaseModel):
    tags: List[GetSimpleInfo]


class WrapGetSubmission(BaseModel):
    submission: GetSubmission


class WrapGetSubmissions(BaseModel):
    submissions: List[GetSubmission]
