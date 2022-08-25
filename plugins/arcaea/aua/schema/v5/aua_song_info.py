from typing import Optional, List
from plugins.arcaea.aua.schema.basemodel import Base
from plugins.arcaea.aua.schema.v5.song_info import SongInfo


class Content(Base):
    song_id: str
    difficulties: List[SongInfo]


class AUASongInfo(Base):
    status: int
    message: Optional[str]
    content: Optional[Content]
