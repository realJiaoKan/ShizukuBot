import requests
import re

from nonebot import on_command, on_regex
from nonebot.typing import T_State
from nonebot.adapters import Event, Bot
from nonebot.adapters.cqhttp import Message

from library.text2pic import *
from plugins.arcaea.database.database import UserInfo, ArcInfo
from plugins.arcaea.message.image_message import UserArcaeaInfo
from plugins.arcaea.aua.api import API
from plugins.arcaea.aua.schema import diffstr2num
from plugins.arcaea.message.text_message import TextMessage

##########[信息]##########
# Arc账号信息 我是个什么东西?
arcaea_account_info = on_command("Arc账号信息")


@arcaea_account_info.handle()
async def _(bot: Bot, event: Event, state: T_State):
    user_info: UserInfo = UserInfo.get_or_none(UserInfo.user_qq == event.user_id)
    if not user_info:
        await arcaea_recent.send("请绑定你的Arcaea帐号")
        return
    arc_info: ArcInfo = ArcInfo.get_or_none(
        ArcInfo.arcaea_id == user_info.arcaea_id
    )
    await arcaea_account_info.send(f"id: {user_info.arcaea_id},用户名: {arc_info.arcaea_name}")


# 曲目信息 < 曲目 > < 难度 > 查询曲目信息
arcaea_song_info = on_command("曲目信息")


@arcaea_song_info.handle()
async def _(bot: Bot, event: Event, state: T_State):
    argv = str(event.get_message()).strip().split(" ")
    if len(argv) < 2:
        await arcaea_song_info.send("请按照正确的消息格式查询谱面预览")
        return
    difficulty = diffstr2num(argv[-1].upper())
    if difficulty is not None:
        songname = " ".join(argv[1:-1])
    else:
        difficulty = -1
        songname = " ".join(argv[1:])
    resp = await API.get_song_info(songname=songname)
    buffer = TextMessage.song_info(data=resp, difficulty=difficulty)
    await arcaea_song_info.send(Message([
        {
            "type": "image",
            "data": {
                "file": f"base64://{str(pic2base64(Image.open(buffer[0])), encoding='utf-8')}"
            }
        },
        {
            "type": "text",
            "data": {
                "text": "\n" + buffer[1]
            }
        }
    ]))


# 谱面预览 < 曲目 > < 难度 > 谱面预览
arcaea_preview = on_command("谱面预览")


@arcaea_preview.handle()
async def _(bot: Bot, event: Event, state: T_State):
    argv = str(event.get_message()).strip().split(" ")
    if len(argv) < 2:
        await arcaea_preview.send("请按照正确的消息格式查询谱面预览")
        return
    difficulty = diffstr2num(argv[-1].upper())
    if difficulty is not None:
        songname = " ".join(argv[1:-1])
    else:
        difficulty = 2
        songname = " ".join(argv[1:])
    resp = await API.get_song_preview(songname=songname, difficulty=difficulty)
    if resp == "ERROR":
        await arcaea_preview.send("未找到谱面预览,请检查歌曲名称是否正确")
        return
    image = Image.open(BytesIO(resp))
    await arcaea_preview.send(Message([
        {
            "type": "image",
            "data": {
                "file": f"base64://{str(pic2base64(image), encoding='utf-8')}"
            }
        }
    ]))


##########[查分]##########
# Arc绑定 < 你的好友码 > 绑定帐号
arcaea_bind = on_command("Arc绑定")


@arcaea_bind.handle()
async def _(bot: Bot, event: Event, state: T_State):
    argv = str(event.get_message()).strip().split(" ")
    if len(argv) != 1 or len(argv[0]) != 9:
        await arcaea_bind.send("请按照正确的消息格式绑定账号")
        return
    arc_id = argv[0]
    arc_info: ArcInfo = ArcInfo.get_or_none(
        (ArcInfo.arcaea_name == arc_id) | (ArcInfo.arcaea_id == arc_id)
    )
    if arc_info:
        arc_id = arc_info.arcaea_id
        arc_name = arc_info.arcaea_name
    resp = await API.get_user_info(arcaea_id=arc_id)
    if error_message := resp.message:
        await arcaea_bind.send("请按照正确的消息格式绑定账号" + error_message)
        return
    arc_id = resp.content.account_info.code
    arc_name = resp.content.account_info.name
    ArcInfo.replace(
        arcaea_id=arc_id,
        arcaea_name=arc_name,
        ptt=resp.content.account_info.rating,
    ).execute()
    UserInfo.delete().where(UserInfo.user_qq == event.user_id).execute()
    UserInfo.replace(user_qq=event.user_id, arcaea_id=arc_id).execute()
    await arcaea_bind.send(f"绑定成功, 用户名: {arc_name}, id: {arc_id}")


# 最近记录 最近一次游玩记录
arcaea_recent = on_command("最近记录")


@arcaea_recent.handle()
async def _(bot: Bot, event: Event, state: T_State):
    user_info: UserInfo = UserInfo.get_or_none(UserInfo.user_qq == event.user_id)
    if not user_info:
        await arcaea_recent.send("请绑定你的Arcaea帐号")
        return
    if UserArcaeaInfo.is_querying(user_info.arcaea_id):
        await arcaea_recent.send("您已在查询队列,请勿重复发起查询")
    result = await UserArcaeaInfo.draw_user_recent(arcaea_id=user_info.arcaea_id)
    await arcaea_recent.send(Message([
        {
            "type": "image",
            "data": {
                "file": f"base64://{str(pic2base64(result), encoding='utf-8')}"
            }
        }
    ]))


# 最佳 < 曲目 > < 难度 > 单曲最佳表现
arcaea_best = on_command("最佳")


@arcaea_best.handle()
async def _(bot: Bot, event: Event, state: T_State):
    argv = str(event.get_message()).strip().split(" ")
    if len(argv) < 2:
        await arcaea_best.send("请按照正确的消息格式查询单曲最佳表现")
        return
    user_info: UserInfo = UserInfo.get_or_none(UserInfo.user_qq == event.user_id)
    difficulty = diffstr2num(argv[-1].upper())
    if difficulty is not None:
        songname = " ".join(argv[1:-1])
    else:
        difficulty = 2
        songname = " ".join(argv[1:])
    if not user_info:
        await arcaea_recent.send("请绑定你的Arcaea帐号")
        return
    if UserArcaeaInfo.is_querying(user_info.arcaea_id):
        await arcaea_recent.send("您已在查询队列,请勿重复发起查询")
    result = await UserArcaeaInfo.draw_user_best(
        arcaea_id=user_info.arcaea_id, songname=songname, difficulty=difficulty
    )
    await arcaea_best.send(Message([
        {
            "type": "image",
            "data": {
                "file": f"base64://{str(pic2base64(result), encoding='utf-8')}"
            }
        }
    ]))


# b30 Best30
arcaea_b30 = on_command("b30")


@arcaea_b30.handle()
async def _(bot: Bot, event: Event, state: T_State):
    user_info: UserInfo = UserInfo.get_or_none(UserInfo.user_qq == event.user_id)
    if not user_info:
        await arcaea_b30.send("请绑定你的Arcaea帐号")
        return
    if UserArcaeaInfo.is_querying(user_info.arcaea_id):
        await arcaea_b30.send("您已在查询队列,请勿重复发起查询")
    result = await UserArcaeaInfo.draw_user_b30(user_info.arcaea_id)
    await arcaea_b30.send(Message([
        {
            "type": "image",
            "data": {
                "file": f"base64://{str(pic2base64(result), encoding='utf-8')}"
            }
        }
    ]))
