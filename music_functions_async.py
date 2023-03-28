from yandex_music import ClientAsync


def authorize():
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
    first_10_songs = result['tracks']['results'][:10]
    answer = ''
    for i in range(len(first_10_songs)):
        answer += f'{i+1}: {(await get_name_with_id(first_10_songs[i]))}\n'
    return answer


async def get_name_for_file(object):  # works
    """Возвращает имя файла, в который сохранится данный обьект при скачивании"""
    return object['title'] + ' - ' + ', '.join(x['name'] for x in object['artists']) + '.mp3'


async def get_name_with_id(object):
    return f"{object['title']} - {', '.join(x['name'] for x in object['artists'])}"


async def get_playlist_name(object):
    return f"{object['title']} - {object['owner']['login']} (найдено {object['track_count']} треков)"


async def download(object, folder):  # works
    """Скачивает данный обьект и возвращает путь к нему"""
    d = await object.download_async(folder + await get_name_for_file(object))


async def get_user_playlists(user_id: str):
    res = await client.users_playlists_list(user_id=user_id)
    return res


async def process_user_playlist_search(result):
    playlists = result  #['playlists']['results']
    ans = ''
    for i in range(len(playlists)):
        ans += f'{i + 1}: {await get_playlist_name(playlists[i])}\n'
    return ans



async def download_playlist(playlist):  # works
    for track in playlist.fetch_tracks_async():
        full_track = await track.fetch_track_async()
        await download(full_track)