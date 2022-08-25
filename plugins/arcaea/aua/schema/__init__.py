from plugins.arcaea.aua.schema.v5.user_info import UserInfo
from plugins.arcaea.aua.schema.v5.user_best30 import UserBest30
from plugins.arcaea.aua.schema.v5.song_info import SongInfo
from plugins.arcaea.aua.schema.v5.score_info import ScoreInfo
from plugins.arcaea.aua.schema.v5.account_info import AccountInfo
from plugins.arcaea.aua.schema.v5.user_best import UserBest
from plugins.arcaea.aua.schema.v5.song_random import SongRandom
from plugins.arcaea.aua.schema.v5.aua_song_info import AUASongInfo


def diffstr2num(diff: str):
    diff_dict = {
        "PAST": 0,
        "PST": 0,
        "PRESENT": 1,
        "PRS": 1,
        "FUTURE": 2,
        "FTR": 2,
        "BEYOND": 3,
        "BYD": 3,
        "ALL": -1,
    }
    return diff_dict.get(diff, None)
