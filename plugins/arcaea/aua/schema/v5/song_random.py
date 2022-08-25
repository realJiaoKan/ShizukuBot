from plugins.arcaea.aua.schema.basemodel import Base
from plugins.arcaea.aua.schema.v5.song_info import SongInfo
from typing import Optional


class Content(Base):
    id: str
    ratingClass: int
    songinfo: SongInfo


class SongRandom(Base):
    status: Optional[int]
    message: Optional[str]
    content: Optional[Content]
