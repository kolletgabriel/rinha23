from datetime import date
from typing import Annotated

from pydantic import BaseModel, StringConstraints, Field


type String32 = Annotated[str, StringConstraints(max_length=32)]
type String100 = Annotated[str, StringConstraints(max_length=100)]
type StackArray = Annotated[list[String32], Field(min_length=1)]


class UserModel(BaseModel):
    nickname: String32
    fullname: String100
    dob: date
    stack: StackArray | None = None

    def to_tuple(self) -> tuple:
        return (self.nickname, self.fullname, self.dob, self.stack)
