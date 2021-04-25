from typing import List, Optional, Tuple
import json
import pycurl
from pydantic import validate_arguments
from io import BytesIO
from ast import literal_eval

from speedo_common.api_schemas import (
    APIBindTags,
    BaseModel,
    PostSubmission,
    Status,
    WrapGetProjects,
    WrapGetSubmission,
    WrapGetSubmissions,
    WrapGetTags,
    WrapGetUsers,
)


class SpeedoError(Exception):
    def __init__(self, message, *, http_status):
        super().__init__(message)
        self.http_status = http_status


class SpeedoClient:
    """
    SpeedoClient creates requests with pycurl because it is faster.
    Speedo is written in fastAPI because it is faster.

    A Mock to SpeedoClient is available
    from speedo_client.mock_client import MockSpeedoClient
    """

    def _speedo_get(self, path: str) -> Tuple[int, BaseModel]:
        url = f"{self._h}{path}"
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        http_response = c.getinfo(pycurl.HTTP_CODE)
        c.close()
        return http_response, literal_eval(buffer.getvalue().decode("UTF-8"))

    def _speedo_post(self, path: str, data: BaseModel) -> Tuple[int, BaseModel]:
        url = f"{self._h}{path}"
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.HTTPHEADER, ["Accept: application/json"])
        c.setopt(pycurl.POSTFIELDS, json.dumps(data))
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        http_response = c.getinfo(pycurl.RESPONSE_CODE)
        c.close()
        return http_response, literal_eval(buffer.getvalue().decode("UTF-8"))

    def _speedo_delete(self, path: str) -> Tuple[int, BaseModel]:
        url = f"{self._h}{path}"
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.CUSTOMREQUEST, "DELETE")
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        http_response = c.getinfo(pycurl.RESPONSE_CODE)
        c.close()
        return http_response, literal_eval(buffer.getvalue().decode("UTF-8"))

    def _return(self, http_code: int, body: BaseModel) -> BaseModel:
        if http_code != 200:
            raise SpeedoError(body["detail"], http_status=http_code)
        return body

    def __init__(self, *, hostname: str) -> None:
        self._h = hostname

    def __str__(self) -> str:
        return self.__doc__

    def get_projects(self) -> WrapGetProjects:
        return WrapGetProjects.parse_obj(
            self._return(*self._speedo_get("/v2/projects"))
        )

    @validate_arguments
    def get_submission(self, uid: str) -> WrapGetSubmission:
        return WrapGetSubmission.parse_obj(
            self._return(*self._speedo_get(f"/v2/submissions/{uid}"))
        )

    def get_submissions(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        mints: Optional[int] = None,
        maxts: Optional[int] = None,
        user: Optional[str] = None,
        project: Optional[str] = None,
        uid: Optional[str] = None,
    ) -> WrapGetSubmissions:
        dd = {
            "limit": limit,
            "offset": offset,
            "mints": mints,
            "maxts": maxts,
            "user": user,
            "project": project,
            "uid": uid,
        }
        url = "/v2/submissions?" + "&".join(
            [f"{k}={v}" for k, v in dd.items() if v is not None]
        )
        return WrapGetSubmissions.parse_obj(self._return(*self._speedo_get(url)))

    def get_tags(self) -> WrapGetTags:
        return WrapGetTags.parse_obj(self._return(*self._speedo_get("/v2/tags")))

    def get_users(self) -> WrapGetUsers:
        return WrapGetUsers.parse_obj(self._return(*self._speedo_get("/v2/users")))

    @validate_arguments
    def post_bind_tags(self, uid: str, tags: List[str]) -> Status:
        data = APIBindTags(tags=tags)
        return Status.parse_obj(
            self._return(*self._speedo_post(f"/v2/submissions/{uid}/tags", data.dict()))
        )

    @validate_arguments
    def post_submission(self, data: PostSubmission) -> Status:
        return Status.parse_obj(
            self._return(*self._speedo_post("/v2/submissions", data.dict()))
        )

    @validate_arguments
    def delete_bind_tag(self, uid: str, tag_name: str) -> Status:
        return Status.parse_obj(
            self._return(*self._speedo_delete(f"/v2/submissions/{uid}/tags/{tag_name}"))
        )

    @validate_arguments
    def delete_bind_tags(self, uid: str) -> Status:
        return Status.parse_obj(
            self._return(*self._speedo_delete(f"/v2/submissions/{uid}/tags"))
        )

    @validate_arguments
    def delete_project(self, name: str) -> Status:
        return Status.parse_obj(
            self._return(*self._speedo_delete(f"/v2/projects/{name}"))
        )

    @validate_arguments
    def delete_submission(self, uid: str) -> Status:
        return Status.parse_obj(
            self._return(*self._speedo_delete(f"/v2/submissions/{uid}"))
        )

    @validate_arguments
    def delete_tag(self, tag_name: str) -> Status:
        return Status.parse_obj(
            self._return(*self._speedo_delete(f"/v2/tags/{tag_name}"))
        )

    @validate_arguments
    def delete_user(self, name: str) -> Status:
        return Status.parse_obj(self._return(*self._speedo_delete(f"/v2/users/{name}")))
