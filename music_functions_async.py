from yandex_music import ClientAsync


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
    first_10_songs = result['tracks']['results'][:10]
    answer = ''
    if len(first_10_songs) == 0:
        return 'Ничего не найдено'
    for i in range(len(first_10_songs)):
        answer += f'{i+1}: {(await get_track_name(first_10_songs[i]))}\n'
    return answer


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
    res = await client.users_playlists_list(user_id=user_id)
    return res


async def process_user_playlist_search(result):
    """Обрабатывает результаты поиска плейлистов и приводит их в понятный пользователю вид"""
    playlists = result  #['playlists']['results']
    ans = ''
    if len(playlists) == 0:
        return 'Ничего не найдено'
    for i in range(len(playlists)):
        ans += f'{i + 1}: {await get_playlist_name(playlists[i])}\n'
    return ans
