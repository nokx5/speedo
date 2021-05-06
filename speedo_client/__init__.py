"""Welcome to the client library of speedo, a fast RESTful web API!

# use the client library
from speedo_client import SpeedoClient
from speedo_client import SpeedoError

pc = SpeedoClient(hostname=hostname)
pc.get_projects()

try:
    pc.delete_users("wrong_input")
except SpeedoError:
    pass

# mock the client library
# requirement : mock and speedo packages
from speedo_client.mock_client import MockSpeedoClient

pc = MockSpeedoClient(hostname=hostname)
pc.get_projects()

try:
    pc.delete_users("wrong_input")
except SpeedoError:
    pass

"""

from speedo_common.version import speedo_version as __version__
from speedo_common.version import interface_version as interface_version

from ._client import SpeedoClient
from ._client import SpeedoError

__all__ = ["SpeedoClient", "SpeedoError"]
