from enum import Enum as _Enum
from collections import namedtuple

from fastapi.exceptions import HTTPException


AssociationError = namedtuple("AssociationError", ["speedo_alert", "http_status"])


class EnumError(_Enum):
    UnknownError = AssociationError("Unknown Error", 403)
    InsertionError = AssociationError("Insertion Error", 409)
    SelectionError = AssociationError("Selection Error", 406)
    DeletionError = AssociationError("Nothing Deleted", 404)
    ForeignKeyError = AssociationError(
        "ForeignKey Conflict, operation is not possible", 409
    )


class SpeedoServerError(Exception):
    def __init__(
        self, *, err: Exception, reason: EnumError = EnumError.UnknownError, **kwargs
    ):
        self.enum_error = reason
        self.kwargs = kwargs
        self.message = f"Speedo Server Error.\n\t\t- Reason : {self.enum_error.value.speedo_alert}.\n\t\t- Additional info : {kwargs}"
        super().__init__(str(err))

    def to_http(self):
        raise HTTPException(self.enum_error.value.http_status, self.message)
