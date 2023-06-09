import asyncio

import yandex_music.exceptions
from yandex_music import ClientAsync
from data.db_class import Db_class
from data.Users_subscription import Users_subscription
from data.db_session import *
from random import randint


def authorize():
    """Авторизация в клиенте"""
    with open('token2.txt', 'r') as tokenfile:
        token = tokenfile.read().strip()
    client = ClientAsync(token)
    client.init()
    return client


client = authorize()


async def search(search_string: str, type_: str = 'all'):
    """Осуществляет поиск по запросу"""
    result = await client.search(search_string, type_=type_)
    return result


async def process_search(result):
    """Обрабатывает результат запроса поиска треков и приводит их в понятный пользователю вид"""
    if result['tracks']:
        first_10_songs = result['tracks']['results'][:10]
        answer = ''
        for i in range(len(first_10_songs)):
            answer += f'{i + 1}: {(await get_track_name(first_10_songs[i]))}\n'
        return answer
    return 'Ничего не найдено'


async def get_name_for_file(object):  # works
    """Возвращает имя файла, в который сохранится данный обьект при скачивании"""
    return object['title'] + ' - ' + ', '.join(x['name'] for x in object['artists']) + '.mp3'


async def get_track_name(object):
    """Возвращает имя трека в виде, понятном пользователю"""
    return f"{object['title']} - {', '.join(x['name'] for x in object['artists'])}"


async def get_playlist_name(object):
    """Возвращает имя плейлиста в виде, понятном пользователю"""
    return f"{object['title']} - {object['owner']['login']} (найдено {object['track_count']} треков)"


async def download(object, folder):  # works
    """Скачивает данный обьект и возвращает путь к нему"""
    d = await object.download_async(folder + await get_name_for_file(object))


async def get_user_playlists(user_id: str):
    """Возвращает обьект результата поиска плейлистов по id пользователя"""
    try:
        res = await client.users_playlists_list(user_id=user_id)
    except yandex_music.exceptions.UnauthorizedError:
        return None
    return res


async def process_user_playlist_search(result):
    """Обрабатывает результаты поиска плейлистов и приводит их в понятный пользователю вид"""
    playlists = result  # ['playlists']['results']
    ans = ''
    if playlists is None:
        return 'Ничего не найдено'
    for i in range(len(playlists)):
        ans += f'{i + 1}: {await get_playlist_name(playlists[i])}\n'
    return ans


async def search_random_track():
    """Возвращает массив с информацией о 10 песнях, которые были выбраны случайно"""
    res = []
    for _ in range(10):
        flag = True
        while flag:
            check = (await client.tracks(track_ids=randint(30000, 1000000)))[0]
            if check['available']:
                res.append(check)
                flag = False
    return res


async def process_search_random_track(tracks):
    """Обрабатывает результаты поиска случайных песен и приводит их в понятный пользователю вид"""
    answer = ''
    for i in range(len(tracks)):
        if tracks[i]["albums"][0]["genre"]:
            answer += f'{i + 1}: {(await get_track_name(tracks[i]))},  жанр - {tracks[i]["albums"][0]["genre"]}\n'
        else:
            answer += f'{i + 1}: {(await get_track_name(tracks[i]))}\n'
    return answer


def get_user_yandex_login(chat_id):
    # cursor = sqlite3.connect('db/database.db').cursor()
    # cursor.execute(f"""SELECT yandex_login FROM login_id_pairs WHERE telegram_chat_id""")
    db_sess = create_session()
    if db_sess.query(Db_class).filter(Db_class.telegram_chat_id == chat_id).first():
        user_yandex_login = db_sess.query(Db_class).filter(Db_class.telegram_chat_id == chat_id).first().yandex_login
        return user_yandex_login


def save_yandex_login(chat_id, login):
    db_sess = create_session()
    data = Db_class()
    data.telegram_chat_id = chat_id
    data.yandex_login = login
    db_sess.add(data)
    db_sess.commit()


def save_subscription(chat_id, login):
    db_sess = create_session()
    data = Users_subscription()
    data.chat_id = chat_id
    data.user = login
    db_sess.add(data)
    db_sess.commit()


def get_id_subscription():
    db_sess = create_session()
    login_subscription = [user_id.chat_id for user_id in db_sess.query(Users_subscription).all()]
    return login_subscription


def delete_subscription(chat_id):
    db_sess = create_session()
    db_sess.query(Users_subscription).filter(Users_subscription.chat_id == chat_id).delete()
    db_sess.commit()


async def search_new_track_chart() -> list:
    """search new track in chart"""
    chart = await client.chart()
    answer = []
    for chart_track in chart['chart']['tracks']:
        if chart_track['chart']['progress'] == 'new' and chart_track['track']['available']:
            answer.append(chart_track)
    if answer:
        return answer
    for chart_track in chart['chart']['tracks']:
        if chart_track['chart']['shift'] >= 4 and chart_track['track']['available']:
            answer.append(chart_track)
    return answer
