def MockSpeedoClient(*, hostname=None) -> "MockSpeedoClient":
    from typing import Tuple

    from mock import Mock
    from fastapi.testclient import TestClient

    from speedo_server.asgi import app
    from speedo_client import SpeedoClient
    from speedo_common.api_schemas import BaseModel

    class MockSpeedoClient(SpeedoClient, Mock):
        client = TestClient(app)
        _h = hostname

        def __init__(self, *, hostname: str) -> None:
            pass

        def _speedo_get(self, path: str) -> Tuple[int, BaseModel]:
            response = self.client.get(path)
            return response.status_code, response.json()

        def _speedo_post(self, path: str, data: BaseModel) -> Tuple[int, BaseModel]:
            response = self.client.post(path, json=data)
            return response.status_code, response.json()

        def _speedo_delete(self, path: str) -> Tuple[int, BaseModel]:
            response = self.client.delete(path)
            return response.status_code, response.json()

    return MockSpeedoClient(hostname=hostname)
