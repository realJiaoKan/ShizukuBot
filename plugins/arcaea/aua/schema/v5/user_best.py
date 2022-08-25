from typing import List, Optional

from plugins.arcaea.aua.schema.basemodel import Base
from plugins.arcaea.aua.schema.v5.score_info import ScoreInfo
from plugins.arcaea.aua.schema.v5.account_info import AccountInfo
from plugins.arcaea.aua.schema.v5.song_info import SongInfo


class Content(Base):
    account_info: AccountInfo
    record: ScoreInfo
    songinfo: List[SongInfo]


class UserBest(Base):
    status: int
    message: Optional[str]
    content: Optional[Content]
