from typing import List, Optional
from plugins.arcaea.aua.schema.basemodel import Base
from plugins.arcaea.aua.schema.v5.account_info import AccountInfo
from plugins.arcaea.aua.schema.v5.song_info import SongInfo
from plugins.arcaea.aua.schema.v5.score_info import ScoreInfo


class Content(Base):
    best30_avg: float
    recent10_avg: float
    account_info: AccountInfo
    best30_list: List[ScoreInfo]
    best30_overflow: List[ScoreInfo]
    best30_songinfo: List[SongInfo]
    best30_overflow_songinfo: List[SongInfo]


class UserBest30(Base):
    status: int
    message: Optional[str]
    content: Optional[Content]
