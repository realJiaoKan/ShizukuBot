import re

from nonebot import on_command, on_regex
from nonebot.typing import T_State
from nonebot.adapters import Event, Bot
from nonebot.adapters.cqhttp import Message

from library.text2pic import *
from plugins.maimai.tool import hash
from plugins.maimai.b40 import generate
from plugins.maimai.b50 import generate50
from plugins.maimai.progress import *
from plugins.setting import *

original_dir = 'assets/maimai/original/'
abstract_dir = 'assets/maimai/abstract/'


# 一些通用函数
def song_txt(music: Music):
    cover_dir = abstract_dir if getSetting('abstract') else original_dir
    return Message([
        {
            "type": "text",
            "data": {
                "text": f"{music.id}. {music.title}\n"
            }
        },
        {
            "type": "image",
            "data": {
                # "file": f"https://www.diving-fish.com/covers/{get_cover_len4_id(music.id)}.png"
                "file": f"base64://{str(pic2base64(Image.open(f'{cover_dir}{get_cover_len4_id(music.id)}.png').convert('RGBA')), encoding='utf-8')}"
            }
        },
        {
            "type": "text",
            "data": {
                "text": f"\n{'/'.join(music.level)}"
            }
        }
    ])


def inner_level_q(ds1, ds2=None):
    result_set = []
    diff_label = ['Bas', 'Adv', 'Exp', 'Mst', 'ReM']
    if ds2 is not None:
        music_data = total_list.filter(ds=(ds1, ds2))
    else:
        music_data = total_list.filter(ds=ds1)
    for music in sorted(music_data, key=lambda i: int(i['id'])):
        for i in music.diff:
            result_set.append((music['id'], music['title'], music['ds'][i], diff_label[i], music['level'][i]))
    return result_set


##########[运势]##########
# 今日舞萌 看看今天人品如何......
wm_list = ['拼机', '推分', '越级', '下埋', '夜勤', '练底力', '练手法', '打旧框', '干饭', '抓绝赞', '收歌']
maimai_jrwm = on_command('今日舞萌')


@maimai_jrwm.handle()
async def _(bot: Bot, event: Event, state: T_State):
    qq = int(event.get_user_id())
    h = hash(qq)
    rp = h % 100
    wm_value = []
    for i in range(11):
        wm_value.append(h & 3)
        h >>= 2
    s = f"今日人品值：{rp}\n"
    for i in range(11):
        if wm_value[i] == 3:
            s += f'宜 {wm_list[i]}\n'
        elif wm_value[i] == 0:
            s += f'忌 {wm_list[i]}\n'
    s += "しずくBot提醒您：打机时不要大力拍打或滑动哦,否则滴蜡熊今晚就来撅你\n今日推荐歌曲："
    music = total_list[h % len(total_list)]
    await maimai_jrwm.finish(Message([
                                         {
                                             "type": "text",
                                             "data": {
                                                 "text": s
                                             }
                                         }
                                     ] + song_txt(music)))


##########[查歌]##########
# <任意字符串>maimai<任意字符串>什么 有什么歌呢?
maimai_maimai_what = on_regex(r".*maimai.*什么")


@maimai_maimai_what.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await maimai_maimai_what.finish(song_txt(total_list.random()))


# 随个(dx||标准)[绿||黄||红||紫||白]<难度> 有什么这样子的歌呢?
maimai_specific_random = on_regex(r"^随个(?:dx|sd|标准)?[绿黄红紫白]?[0-9]+\+?")


@maimai_specific_random.handle()
async def _(bot: Bot, event: Event, state: T_State):
    level_labels = ['绿', '黄', '红', '紫', '白']
    regex = "随个((?:dx|sd|标准))?([绿黄红紫白]?)([0-9]+\+?)"
    res = re.match(regex, str(event.get_message()).lower())
    try:
        if res.groups()[0] == "dx":
            tp = ["DX"]
        elif res.groups()[0] == "sd" or res.groups()[0] == "标准":
            tp = ["SD"]
        else:
            tp = ["SD", "DX"]
        level = res.groups()[2]
        if res.groups()[1] == "":
            music_data = total_list.filter(level=level, type=tp)
        else:
            music_data = total_list.filter(level=level, diff=['绿黄红紫白'.index(res.groups()[1])], type=tp)
        if len(music_data) == 0:
            rand_result = "没有这样的乐曲哦。"
        else:
            rand_result = song_txt(music_data.random())
        await maimai_specific_random.send(rand_result)
    except Exception as e:
        print(e)
        await maimai_specific_random.finish("随机命令错误，请检查语法")


# 查歌<乐曲标题的一部分> 这是什么歌?
maimai_search_song = on_regex(r"^查歌.+")


@maimai_search_song.handle()
async def _(bot: Bot, event: Event, state: T_State):
    regex = "查歌(.+)"
    name = re.match(regex, str(event.get_message())).groups()[0].strip()
    if name == "":
        return
    res = total_list.filter(title_search=name)
    if len(res) == 0:
        await maimai_search_song.send("没有找到这样的乐曲。")
    elif len(res) < 50:
        search_result = ""
        for music in sorted(res, key=lambda i: int(i['id'])):
            search_result += f"{music['id']}. {music['title']}\n"
        await maimai_search_song.finish(Message([
            {
                "type": "text",
                "data": {
                    "text": search_result.strip()
                }
            }]))
    else:
        await maimai_search_song.send(f"结果过多（{len(res)} 条），请缩小查询范围。")


# <歌曲别名>是什么歌 是什么歌呢?(这东西mai-bot项目里貌似没有写实现......)
# 定数查歌 [<定数>||<定数下限> <定数上限>] 查询定数对应的乐曲
maimai_level_song_query = on_command('定数查歌')


@maimai_level_song_query.handle()
async def _(bot: Bot, event: Event, state: T_State):
    argv = str(event.get_message()).strip().split(" ")
    if len(argv) > 2 or len(argv) == 0:
        await maimai_level_song_query.finish("命令格式为\n定数查歌 <定数>\n定数查歌 <定数下限> <定数上限>")
        return
    if len(argv) == 1:
        result_set = inner_level_q(float(argv[0]))
    else:
        result_set = inner_level_q(float(argv[0]), float(argv[1]))
    if len(result_set) > 50:
        await maimai_level_song_query.finish(f"结果过多（{len(result_set)} 条），请缩小搜索范围。")
        return
    s = ""
    for elem in result_set:
        s += f"{elem[0]}. {elem[1]} {elem[3]} {elem[4]}({elem[2]})\n"
    await maimai_level_song_query.finish(s.strip())


##########[信息]##########
# [绿||黄||红||紫||白]id<歌曲编号> 查询乐曲信息或谱面信息
maimai_query_chart = on_regex(r"^([绿黄红紫白]?)id([0-9]+)")


@maimai_query_chart.handle()
async def _(bot: Bot, event: Event, state: T_State):
    cover_dir = abstract_dir if getSetting('abstract') else original_dir
    regex = "([绿黄红紫白]?)id([0-9]+)"
    groups = re.match(regex, str(event.get_message())).groups()
    level_labels = ['绿', '黄', '红', '紫', '白']
    if groups[0] != "":
        try:
            level_index = level_labels.index(groups[0])
            level_name = ['Basic', 'Advanced', 'Expert', 'Master', 'Re: MASTER']
            name = groups[1]
            music = total_list.by_id(name)
            chart = music['charts'][level_index]
            ds = music['ds'][level_index]
            level = music['level'][level_index]
            file = f"base64://{str(pic2base64(Image.open(f'{cover_dir}{get_cover_len4_id(music.id)}.png').convert('RGBA')), encoding='utf-8')}"
            if len(chart['notes']) == 4:
                msg = f'''{level_name[level_index]} {level}({ds})
TAP: {chart['notes'][0]}
HOLD: {chart['notes'][1]}
SLIDE: {chart['notes'][2]}
BREAK: {chart['notes'][3]}
谱师: {chart['charter']}'''
            else:
                msg = f'''{level_name[level_index]} {level}({ds})
TAP: {chart['notes'][0]}
HOLD: {chart['notes'][1]}
SLIDE: {chart['notes'][2]}
TOUCH: {chart['notes'][3]}
BREAK: {chart['notes'][4]}
谱师: {chart['charter']}'''
            await maimai_query_chart.send(Message([
                {
                    "type": "text",
                    "data": {
                        "text": f"{music['id']}. {music['title']}\n"
                    }
                },
                {
                    "type": "image",
                    "data": {
                        "file": f"{file}"
                    }
                },
                {
                    "type": "text",
                    "data": {
                        "text": '\n' + msg
                    }
                }
            ]))
        except Exception:
            await maimai_query_chart.send("未找到该谱面")
    else:
        name = groups[1]
        music = total_list.by_id(name)
        try:
            file = f"base64://{str(pic2base64(Image.open(f'{cover_dir}{get_cover_len4_id(music.id)}.png').convert('RGBA')), encoding='utf-8')}"
            await maimai_query_chart.send(Message([
                {
                    "type": "text",
                    "data": {
                        "text": f"{music['id']}. {music['title']}\n"
                    }
                },
                {
                    "type": "image",
                    "data": {
                        "file": f"{file}"
                    }
                },
                {
                    "type": "text",
                    "data": {
                        "text": f"\n艺术家: {music['basic_info']['artist']}\n分类: {music['basic_info']['genre']}\nBPM: {music['basic_info']['bpm']}\n版本: {music['basic_info']['from']}\n难度: {'/'.join(music['level'])}"
                    }
                }
            ]))
        except Exception:
            await maimai_query_chart.send("未找到该乐曲")


# 舞萌分数线 <难度+歌曲id> <分数线> 详情请输入“舞萌分数线 帮助”查看
maimai_cut_off_point = on_command('舞萌分数线')


@maimai_cut_off_point.handle()
async def _(bot: Bot, event: Event, state: T_State):
    r = "([绿黄红紫白])(id)?([0-9]+)"
    argv = str(event.get_message()).strip().split(" ")
    if len(argv) == 1 and argv[0] == '帮助':
        s = '''舞萌分数线计算器说明书:
命令格式:舞萌分数线 <难度+歌曲id> <分数线>
例如：分数线 紫799 100
命令将返回分数线允许的 TAP GREAT 容错以及 BREAK 50落等价的 TAP GREAT 数。
以下为 TAP GREAT 的对应表:
|      GREAT / GOOD / MISS
|TAP     1   / 2.5  /  5
|HOLD    2   /  5   /  10
|SLIDE   3   / 7.5  /  15
|TOUCH   1   / 2.5  /  5
|BREAK   5   / 12.5 /  25
(外加200落)'''
        await maimai_cut_off_point.send(Message([{
            "type": "image",
            "data": {
                "file": f"base64://{str(pic2base64(text2pic(s)), encoding='utf-8')}"
            }
        }]))
    elif len(argv) == 2:
        try:
            grp = re.match(r, argv[0]).groups()
            level_labels = ['绿', '黄', '红', '紫', '白']
            level_labels2 = ['Basic', 'Advanced', 'Expert', 'Master', 'Re:MASTER']
            level_index = level_labels.index(grp[0])
            chart_id = grp[2]
            line = float(argv[1])
            music = total_list.by_id(chart_id)
            chart: Dict[Any] = music['charts'][level_index]
            tap = int(chart['notes'][0])
            slide = int(chart['notes'][2])
            hold = int(chart['notes'][1])
            touch = int(chart['notes'][3]) if len(chart['notes']) == 5 else 0
            brk = int(chart['notes'][-1])
            total_score = 500 * tap + slide * 1500 + hold * 1000 + touch * 500 + brk * 2500
            break_bonus = 0.01 / brk
            break_50_reduce = total_score * break_bonus / 4
            reduce = 101 - line
            if reduce <= 0 or reduce >= 101:
                raise ValueError
            await maimai_query_chart.send(f'''{music['title']} {level_labels2[level_index]}
分数线 {line}% 允许的最多 TAP GREAT 数量为 {(total_score * reduce / 10000):.2f}(每个-{10000 / total_score:.4f}%),
BREAK 50落(一共{brk}个)等价于 {(break_50_reduce / 100):.3f} 个 TAP GREAT(-{break_50_reduce / total_score * 100:.4f}%)''')
        except Exception:
            await maimai_query_chart.send("格式错误,输入“舞萌分数线 帮助”以查看帮助信息")


##########[查分]##########
# b40 Best40
maimai_b40 = on_command('b40')


@maimai_b40.handle()
async def _(bot: Bot, event: Event, state: T_State):
    username = str(event.get_message()).strip()
    if username == "":
        payload = {
            'qq': str(event.get_user_id())
        }
    else:
        payload = {
            'username': username
        }
    img, success = await generate(payload)
    if success == 400:
        await maimai_b40.send("未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
    elif success == 403:
        await maimai_b40.send("该用户禁止了其他人获取数据。")
    else:
        await maimai_b40.send(Message([
            {
                "type": "image",
                "data": {
                    "file": f"base64://{str(pic2base64(img), encoding='utf-8')}"
                }
            }
        ]))


# b50 Best50
best_50_pic = on_command('b50')


@best_50_pic.handle()
async def _(bot: Bot, event: Event, state: T_State):
    username = str(event.get_message()).strip()
    if username == "":
        payload = {
            'qq': str(event.get_user_id()),
            'b50': True
        }
    else:
        payload = {
            'username': username,
            'b50': True
        }
    img, success = await generate50(payload)
    if success == 400:
        await best_50_pic.send("未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
    elif success == 403:
        await best_50_pic.send("该用户禁止了其他人获取数据。")
    else:
        await best_50_pic.send(Message([
            {
                "type": "image",
                "data": {
                    "file": f"base64://{str(pic2base64(img), encoding='utf-8')}"
                }
            }
        ]))


##########[进度]##########
# 进度 <版本牌子代号> <后缀> 查看牌子完成进度
reward_progress = on_command('进度')


@reward_progress.handle()
async def _(bot: Bot, event: Event, state: T_State):
    qqid = event.get_user_id()
    argv = str(event.get_message()).strip().split(" ")

    if len(argv) != 2:
        await reward_progress.send("真超檄橙暁晓桃櫻樱紫菫堇白雪輝辉熊華华爽舞霸\n極极将舞神者舞舞")
        return
    if argv[0] == '真' and argv[1] == '将':
        await reward_progress.send("真系没有真将哦")
        return
    payload = {
        'qq': qqid
    }

    if argv[0] in ['霸', '舞']:
        payload['version'] = list(set(version for version in list(plate_to_version.values())[:-5]))
    else:
        payload['version'] = [plate_to_version[argv[0]]]

    data = await player_plate_data(payload, [argv[0], argv[1]])
    await  reward_progress.send(data)
