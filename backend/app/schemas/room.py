from typing import Literal

from pydantic import BaseModel


RoomType = Literal["free_area", "topic_room"]


class RoomRead(BaseModel):
    id: int
    code: str
    name: str
    room_type: RoomType
    capacity: int
    campus_code: str | None
    building: str | None
    location: str | None
    is_active: bool


class RoomListResponse(BaseModel):
    items: list[RoomRead]
    limit: int
    offset: int
    total: int
