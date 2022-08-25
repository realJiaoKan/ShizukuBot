from plugins.maimai.music import *

SONGS_PER_PAGE = 25
level_labels = ['绿', '黄', '红', '紫', '白']
scoreRank = 'D C B BB BBB A AA AAA S S+ SS SS+ SSS SSS+'.lower().split(' ')
comboRank = 'FC FC+ AP AP+'.lower().split(' ')
combo_rank = 'fc fcp ap app'.split(' ')
syncRank = 'FS FS+ FDX FDX+'.lower().split(' ')
sync_rank = 'fs fsp fsd fsdp'.split(' ')
diffs = 'Basic Advanced Expert Master Re:Master'.split(' ')
levelList = '1 2 3 4 5 6 7 7+ 8 8+ 9 9+ 10 10+ 11 11+ 12 12+ 13 13+ 14 14+ 15'.split(' ')
achievementList = [50.0, 60.0, 70.0, 75.0, 80.0, 90.0, 94.0, 97.0, 98.0, 99.0, 99.5, 100.0, 100.5]
BaseRa = [0.0, 5.0, 6.0, 7.0, 7.5, 8.5, 9.5, 10.5, 12.5, 12.7, 13.0, 13.2, 13.5, 14.0]
BaseRaSpp = [7.0, 8.0, 9.6, 11.2, 12.0, 13.6, 15.2, 16.8, 20.0, 20.3, 20.8, 21.1, 21.6, 22.4]
realAchievementList = {}
plate_to_version = {
    '初': 'maimai',
    '真': 'maimai PLUS',
    '超': 'maimai GreeN',
    '檄': 'maimai GreeN PLUS',
    '橙': 'maimai ORANGE',
    '暁': 'maimai ORANGE PLUS',
    '晓': 'maimai ORANGE PLUS',
    '桃': 'maimai PiNK',
    '櫻': 'maimai PiNK PLUS',
    '樱': 'maimai PiNK PLUS',
    '紫': 'maimai MURASAKi',
    '菫': 'maimai MURASAKi PLUS',
    '堇': 'maimai MURASAKi PLUS',
    '白': 'maimai MiLK',
    '雪': 'MiLK PLUS',
    '輝': 'maimai FiNALE',
    '辉': 'maimai FiNALE',
    '熊': 'maimai でらっくす',
    '華': 'maimai でらっくす',
    '华': 'maimai でらっくす',
    '華': 'maimai でらっくす PLUS',
    '华': 'maimai でらっくす PLUS',
    '爽': 'maimai でらっくす Splash',
    '煌': 'maimai でらっくす Splash',
    '煌': 'maimai でらっくす Splash PLUS',
}


async def get_player_data(project: str, payload: dict) -> Union[dict, str]:
    """
    获取用户数据，获取失败时返回字符串
    - `project` : 项目
        - `best` : 玩家数据
        - `plate` : 牌子
    - `payload` : 传递给查分器的数据
    """
    if project == 'best':
        p = 'player'
    elif project == 'plate':
        p = 'plate'
    else:
        return '项目错误'
    try:
        async with aiohttp.request('POST', f'https://www.diving-fish.com/api/maimaidxprober/query/{p}',
                                   json=payload) as resp:
            if resp.status == 400:
                data = '未找到此玩家,请确保此玩家的用户名和查分器中的用户名相同'
            elif resp.status == 403:
                data = '该用户禁止了其他人获取数据'
            elif resp.status == 200:
                data = await resp.json()
            else:
                data = '未知错误'
    except Exception as e:
        data = f'获取玩家数据时发生错误:{type(e)}'
    return data


async def player_plate_data(payload: dict, type: str):
    song_played = []
    song_remain_basic = []
    song_remain_advanced = []
    song_remain_expert = []
    song_remain_master = []
    song_remain_re_master = []
    song_remain_difficult = []

    data = await get_player_data('plate', payload)

    if isinstance(data, str):
        return data

    if type[1] in ['将', '者']:
        for song in data['verlist']:
            if song['level_index'] == 0 and song['achievements'] < (100.0 if type[1] == '将' else 80.0):
                song_remain_basic.append([song['id'], song['level_index']])
            if song['level_index'] == 1 and song['achievements'] < (100.0 if type[1] == '将' else 80.0):
                song_remain_advanced.append([song['id'], song['level_index']])
            if song['level_index'] == 2 and song['achievements'] < (100.0 if type[1] == '将' else 80.0):
                song_remain_expert.append([song['id'], song['level_index']])
            if song['level_index'] == 3 and song['achievements'] < (100.0 if type[1] == '将' else 80.0):
                song_remain_master.append([song['id'], song['level_index']])
            if type[0] in ['舞', '霸'] and song['level_index'] == 4 and song['achievements'] < (
                    100.0 if type[1] == '将' else 80.0):
                song_remain_re_master.append([song['id'], song['level_index']])
            song_played.append([song['id'], song['level_index']])
    elif type[1] in ['極', '极']:
        for song in data['verlist']:
            if song['level_index'] == 0 and not song['fc']:
                song_remain_basic.append([song['id'], song['level_index']])
            if song['level_index'] == 1 and not song['fc']:
                song_remain_advanced.append([song['id'], song['level_index']])
            if song['level_index'] == 2 and not song['fc']:
                song_remain_expert.append([song['id'], song['level_index']])
            if song['level_index'] == 3 and not song['fc']:
                song_remain_master.append([song['id'], song['level_index']])
            if type[0] == '舞' and song['level_index'] == 4 and not song['fc']:
                song_remain_re_master.append([song['id'], song['level_index']])
            song_played.append([song['id'], song['level_index']])
    elif type[1] == '舞舞':
        for song in data['verlist']:
            if song['level_index'] == 0 and song['fs'] not in ['fsd', 'fsdp']:
                song_remain_basic.append([song['id'], song['level_index']])
            if song['level_index'] == 1 and song['fs'] not in ['fsd', 'fsdp']:
                song_remain_advanced.append([song['id'], song['level_index']])
            if song['level_index'] == 2 and song['fs'] not in ['fsd', 'fsdp']:
                song_remain_expert.append([song['id'], song['level_index']])
            if song['level_index'] == 3 and song['fs'] not in ['fsd', 'fsdp']:
                song_remain_master.append([song['id'], song['level_index']])
            if type[0] == '舞' and song['level_index'] == 4 and song['fs'] not in ['fsd', 'fsdp']:
                song_remain_re_master.append([song['id'], song['level_index']])
            song_played.append([song['id'], song['level_index']])
    elif type[1] == '神':
        for song in data['verlist']:
            if song['level_index'] == 0 and song['fc'] not in ['ap', 'app']:
                song_remain_basic.append([song['id'], song['level_index']])
            if song['level_index'] == 1 and song['fc'] not in ['ap', 'app']:
                song_remain_advanced.append([song['id'], song['level_index']])
            if song['level_index'] == 2 and song['fc'] not in ['ap', 'app']:
                song_remain_expert.append([song['id'], song['level_index']])
            if song['level_index'] == 3 and song['fc'] not in ['ap', 'app']:
                song_remain_master.append([song['id'], song['level_index']])
            if type[0] == '舞' and song['level_index'] == 4 and song['fc'] not in ['ap', 'app']:
                song_remain_re_master.append([song['id'], song['level_index']])
            song_played.append([song['id'], song['level_index']])
    for music in total_list:
        if music.version in payload['version']:
            if [int(music.id), 0] not in song_played:
                song_remain_basic.append([int(music.id), 0])
            if [int(music.id), 1] not in song_played:
                song_remain_advanced.append([int(music.id), 1])
            if [int(music.id), 2] not in song_played:
                song_remain_expert.append([int(music.id), 2])
            if [int(music.id), 3] not in song_played:
                song_remain_master.append([int(music.id), 3])
            if type[0] in ['舞', '霸'] and len(music.level) == 5 and [int(music.id), 4] not in song_played:
                song_remain_re_master.append([int(music.id), 4])
    song_remain_basic = sorted(song_remain_basic, key=lambda i: int(i[0]))
    song_remain_advanced = sorted(song_remain_advanced, key=lambda i: int(i[0]))
    song_remain_expert = sorted(song_remain_expert, key=lambda i: int(i[0]))
    song_remain_master = sorted(song_remain_master, key=lambda i: int(i[0]))
    song_remain_re_master = sorted(song_remain_re_master, key=lambda i: int(i[0]))
    for song in song_remain_basic + song_remain_advanced + song_remain_expert + song_remain_master + song_remain_re_master:
        music = total_list.by_id(str(song[0]))
        if music.ds[song[1]] > 13.6:
            song_remain_difficult.append(
                [music.id,
                 music.title,
                 diffs[song[1]],
                 music.ds[song[1]],
                 music.stats[song[1]].difficulty,
                 song[1]])

    appellation = '您'

    msg = f'''{appellation}的{type[0]}{type[1]}剩余进度如下:
Basic剩余{len(song_remain_basic)}首
Advanced剩余{len(song_remain_advanced)}首
Expert剩余{len(song_remain_expert)}首
Master剩余{len(song_remain_master)}首
'''
    song_remain: list[
        list] = song_remain_basic + song_remain_advanced + song_remain_expert + song_remain_master + song_remain_re_master
    song_record = [[s['id'], s['level_index']] for s in data['verlist']]
    if type[0] in ['舞', '霸']:
        msg += f'Re:Master剩余{len(song_remain_re_master)}首\n'
    if len(song_remain_difficult) > 0:
        if len(song_remain_difficult) < 60:
            msg += '剩余定数大于13.6的曲目:\n'
            for i, s in enumerate(sorted(song_remain_difficult, key=lambda i: i[3])):
                self_record = ''
                if [int(s[0]), s[-1]] in song_record:
                    record_index = song_record.index([int(s[0]), s[-1]])
                    if type[1] in ['将', '者']:
                        self_record = str(data['verlist'][record_index]['achievements']) + '%'
                    elif type[1] in ['極', '极', '神']:
                        if data['verlist'][record_index]['fc']:
                            self_record = comboRank[combo_rank.index(data['verlist'][record_index]['fc'])].upper()
                    elif type[1] == '舞舞':
                        if data['verlist'][record_index]['fs']:
                            self_record = syncRank[sync_rank.index(data['verlist'][record_index]['fs'])].upper()
                msg += f'No.{i + 1} {s[0]}. {s[1]} {s[2]} {s[3]} {s[4]} {self_record}'.strip() + '\n'
        else:
            msg += f'还有{len(song_remain_difficult)}首大于13.6定数的曲目，加油推分捏!\n'
    elif len(song_remain) > 0:
        for i, s in enumerate(song_remain):
            m = total_list.by_id(str(s[0]))
            ds = m.ds[s[1]]
            song_remain[i].append(ds)
        if len(song_remain) < 60:
            msg += '剩余曲目:\n'
            for i, s in enumerate(sorted(song_remain, key=lambda i: i[2])):
                m = total_list.by_id(str(s[0]))
                self_record = ''
                if [int(s[0]), s[-1]] in song_record:
                    record_index = song_record.index([int(s[0]), s[-1]])
                    if type[1] in ['将', '者']:
                        self_record = str(data['verlist'][record_index]['achievements']) + '%'
                    elif type[1] in ['極', '极', '神']:
                        if data['verlist'][record_index]['fc']:
                            self_record = comboRank[combo_rank.index(data['verlist'][record_index]['fc'])].upper()
                    elif type[1] == '舞舞':
                        if data['verlist'][record_index]['fs']:
                            self_record = syncRank[sync_rank.index(data['verlist'][record_index]['fs'])].upper()
                msg += f'No.{i + 1} {m.id}. {m.title} {diffs[s[1]]} {m.ds[s[1]]} {m.stats[s[1]].difficulty} {self_record}'.strip() + '\n'
        else:
            msg += '已经没有定数大于13.6的曲目了,加油清谱捏!\n'
    else:
        msg += f'恭喜{appellation}完成{type[0]}{type[1]}!'
    msg += 'by しずくBot'
    return msg
