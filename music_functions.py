from yandex_music import Client


def authorize():
    with open('token2.txt', 'r') as tokenfile:
        token = tokenfile.read().strip()
    cl = Client(token).init()
    return cl


client = authorize()


def search(search_string: str, type_: str = 'all'):
    """Осуществляет поиск по запросу"""
    result = client.search(search_string, type_=type_)
    return result


def get_name_for_file(object):  # works
    """Возвращает имя файла, в который сохранится данный обьект при скачивании"""
    return object['title'] + ' - ' + ', '.join(x['name'] for x in object['artists']) + '.mp3'


def download(object):  # works
    """Скачивает данный обьект и возвращает путь к нему"""
    d = object.download(get_name_for_file(object))


def get_user_playlists(user_id: str):
    res = client.users_playlists_list(user_id=user_id)
    return res


def download_playlist(playlist):  # works
    for track in playlist.fetch_tracks():
        full_track = track.fetch_track()
        # client.tracks_download_info(track_id=full_track['id'])
        # full_track.download(get_name_for_file(full_track))
        download(full_track)
        print(get_name_for_file(full_track), 'was downloaded')