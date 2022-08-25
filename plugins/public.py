import random

from nonebot import on_command, on_notice
from nonebot.adapters.cqhttp import Message, Event, Bot
from nonebot.exception import IgnoredException
from nonebot.message import event_preprocessor
from nonebot.typing import T_State

from library.text2pic import *


# 不回复临时对话
@event_preprocessor
async def preprocessor(bot, event, state):
    if hasattr(event, 'message_type') and event.message_type == "private" and event.sub_type != "friend":
        raise IgnoredException("not reply group temp message")


# help
help = on_command('help')


@help.handle()
async def _(bot: Bot, event: Event, state: T_State):
    help_str = '''请用以下格式之消息召唤しずくちゃん~:
说明:
|  () Optional
|  <> Required
|  || Or
|  [] Block
    每行最后一个空格后是备注,但是命令中的空格别忘记填写
舞萌DX(合并自mai-bot项目):
    [运势]
    今日舞萌 看看今天人品如何......
    [查歌]
    <任意字符串>maimai<任意字符串>什么 有什么歌呢?
    随个(dx||标准)[绿||黄||红||紫||白]<难度> 有什么这样子的歌呢?
    查歌<乐曲标题的一部分> 这是什么歌?
    <歌曲别名>是什么歌 是什么歌呢?(这东西mai-bot项目里貌似没有写实现......)
    定数查歌 [<定数>||<定数下限> <定数上限>] 查询定数对应的乐曲
    [信息]
    [绿||黄||红||紫||白]id<歌曲编号> 查询乐曲信息或谱面信息
    舞萌分数线 <难度+歌曲id> <分数线> 详情请输入"舞萌分数线 帮助"查看
    [查分]
    b40 Best40
    b50 Best50
    [进度]
    进度 <版本牌子代号> <后缀> 查看牌子完成进度(发送"进度"可获得代号列表)
韵律原点(基于AUA):
    [信息]
    Arc账号信息 我是个什么东西?
    曲目信息 <曲目> <难度> 查询曲目信息
    谱面预览 <曲目> <难度> 谱面预览
    [查分]
    Arc绑定 <你的好友码> 绑定帐号
    最近记录 最近一次游玩记录
    最佳 <曲目> <难度> 单曲最佳表现
    b30 Best30
中二节奏://等待开服中......
    [查歌]
    [信息]
    [查分]
其它命令://开发中,v我50可以加速开发捏'''
    await help.send(Message([{
        "type": "image",
        "data": {
            "file": f"base64://{str(pic2base64(text2pic(help_str)), encoding='utf-8')}"
        }
    }]))


async def _group_poke(bot: Bot, event: Event, state: dict) -> bool:
    value = (event.notice_type == "notify" and event.sub_type == "poke" and event.target_id == int(bot.self_id))
    return value


# 戳一戳
saoSpeech = ['雅蠛蝶~~',
             '戳什么戳,看我戳你小鸟~',
             'やめてください~~',
             '你看我,扎不扎你,就完了',
             '再戳就吃你绝赞',
             '你绝赞绿了',
             '你蛇红了',
             '你脑袋绿了',
             '激情舞蹈👉https://www.youtube.com/watch?v=dQw4w9WgXcQ',
             '熟女热舞👉https://www.bilibili.com/video/BV1GJ411x7h7',
             'NeVer goNNa GIvE yOu uP~~',
             'Creeper~']
poke = on_notice(rule=_group_poke, priority=10, block=True)


@poke.handle()
async def _(bot: Bot, event: Event, state: T_State):
    if event.__getattribute__('group_id') is None:
        event.__delattr__('group_id')
    await poke.send(Message([{
        "type": "poke",
        "data": {
            "qq": f"{event.sender_id}"
        }
    }]))
    await poke.send(random.choice(saoSpeech))
