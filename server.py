# Импортируем необходимые классы.
# import asyncio.exceptions
from concurrent.futures import TimeoutError
import logging
import os

import telegram.error
import yandex_music.exceptions
from telegram.ext import Application, MessageHandler, filters, ConversationHandler

import music_functions_async
from Token import BOT_TOKEN
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup, InputMediaPhoto, MenuButtonCommands, MenuButton, ReplyKeyboardRemove, \
    MenuButtonWebApp, \
    InlineKeyboardButton, InlineKeyboardMarkup, MenuButton

from data import db_session

db_session.global_init("db/database.db")

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)


# Эта строка отсылает сообщение
async def start_dialog_search_playlists(update, context):
    """Обработчик первой стадии диалога поиска плейлистов, начало диалога"""
    await update.message.reply_text('Укажите логин пользователя. Для выхода из диалога введите /stop')
    return 1


async def search_users_playlists(update, context):
    """Обработчик второй стадии диалога поиска плейлистов, выполняет поиск по id"""
    user_id = update.message.text
    res = await music_functions_async.get_user_playlists(user_id)
    ans = await music_functions_async.process_user_playlist_search(res)
    await update.message.reply_text(ans)
    if ans == 'Ничего не найдено':
        await update.message.reply_text('Убедитесь в корректности введенных данных и попробуйте снова')
        return ConversationHandler.END
    await update.message.reply_text('Для скачивания плейлиста укажите его номер'
                                    ' в данном списке. Для выхода из диалога введите /stop')
    context.chat_data['user_id'] = user_id
    context.chat_data['playlists_amount'] = len(res)
    context.chat_data['result'] = res
    return 2


async def ask_for_playlist_download(update, context):
    """Обработчик третий стадии диалога поиска плейлистов, получение номера требуемого плейлиста"""
    try:
        num = int(update.message.text)
    except ValueError:
        await update.message.reply_text('Введен неверный номер, попробуйте снова')
        return 1
    if num > context.chat_data['playlists_amount']:
        await update.message.reply_text('Введен слишком большой номер, попробуйте снова')
        return 1
    await update.message.reply_text(f'Вы точно хотите скачать плейлист\n '
                                    f'{await music_functions_async.get_playlist_name(context.chat_data["result"][num - 1])}?\n'
                                    f'Введите да, если хотите скачать плейлист, и любой другой ответ в ином случае',
                                    reply_markup=markup_search)
    context.chat_data['num'] = num
    return 3


async def download_playlist(update, context):
    """Обработчик третьей стадии диалога поиска плейлистов, скачивание плейлиста"""
    if update.message.text.lower() != 'да':
        await update.message.reply_text('Скачивание отменено', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    await update.message.reply_text('Скачиваем...', reply_markup=ReplyKeyboardRemove())
    playlist = context.chat_data['result'][context.chat_data['num'] - 1]
    with open('timeouts.txt', 'w') as timeouts:
        for track in (await music_functions_async.client.users_playlists(playlist.kind, playlist.owner.uid)).tracks:
            full_track = await track.fetch_track_async()
            got_file = False
            while not got_file:
                try:
                    await music_functions_async.download(full_track,
                                                         folder='downloads/')
                    got_file = True
                except (yandex_music.exceptions.TimedOutError, TimeoutError):
                    continue
            await update.message.reply_text(f'{full_track["title"]} отправляется...')
            file_sent = False
            while not file_sent:
                try:
                    await context.bot.send_document(
                        document=open(f'downloads/{await music_functions_async.get_name_for_file(full_track)}', 'rb'),
                        chat_id=update.message.chat_id,
                        read_timeout=20, write_timeout=20, connect_timeout=20, pool_timeout=20)
                    file_sent = True
                    timeouts.write(f'[OK]{await music_functions_async.get_name_for_file(full_track)}\n')
                except (
                        telegram.error.TimedOut, TimeoutError,
                        yandex_music.exceptions.TimedOutError):
                    timeouts.write(f'[ERR]{await music_functions_async.get_name_for_file(full_track)} time-out\n')
                    continue

            os.remove(f'downloads/{await music_functions_async.get_name_for_file(full_track)}')

    # скачиваем плейлист
    return ConversationHandler.END


async def start_dialog_search_track(update, context):
    """Обработчик первой стадии диалога поиска треков, начинает диалог"""
    await update.message.reply_text(
        'Введите запрос (в качестве запроса может быть: название трека, его автор или текст из этой песни). Для выхода из диалога введите /stop')
    return 1


async def search_track(update, context):
    """Обработчик второй стадии диалога поиска треков, поиск трека"""
    search_string = update.message.text.strip()  # 12 - длина команды
    search_result = await music_functions_async.search(search_string)
    answer = await music_functions_async.process_search(search_result)
    await update.message.reply_text(answer)
    if answer == 'Ничего не найдено':
        await update.message.reply_text('Убедитесь в корректности введенных данных и попробуйте снова')
        return ConversationHandler.END
    await update.message.reply_text(
        'Для скачивания трека введите его номер в этом списке. Для выхода из диалога введите /stop')
    context.chat_data['result'] = search_result['tracks']['results']
    return 2


async def ask_for_track_download(update, context):
    """Обработчик третьей стадии поиска треков, отвечает за получение номера скачиваемого трека"""
    try:
        num = int(update.message.text)
    except ValueError:
        await update.message.reply_text('Введен неверный номер, попробуйте снова')
        return 2
    if num > 10:
        await update.message.reply_text('Введен слишком большой номер, попробуйте снова')
        return 2
    await update.message.reply_text(f'Вы точно хотите скачать трек\n '
                                    f'{await music_functions_async.get_track_name(context.chat_data["result"][num - 1])}?\n'
                                    f'Введите да, если хотите скачать трек, и любой другой ответ в ином случае',
                                    reply_markup=markup_search)
    context.chat_data['num'] = num
    return 3


async def download_track(update, context):
    """Обработчик четвертой стадии диалога поиска треков, скачивание трека"""
    if update.message.text.lower() != 'да':
        await update.message.reply_text('Скачивание отменено', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    await update.message.reply_text('Скачиваем...', reply_markup=ReplyKeyboardRemove())
    full_track = context.chat_data['result'][context.chat_data['num'] - 1]
    got_file = False
    while not got_file:
        try:
            await music_functions_async.download(full_track,
                                                 folder='downloads/')
            got_file = True
        except (yandex_music.exceptions.TimedOutError, TimeoutError):
            continue
    # await music_functions_async.download(full_track, folder='downloads/')
    await update.message.reply_text(f'{await music_functions_async.get_track_name(full_track)} отправляется...')
    file_sent = False
    while not file_sent:
        try:
            await context.bot.send_document(
                document=open(f'downloads/{await music_functions_async.get_name_for_file(full_track)}', 'rb'),
                chat_id=update.message.chat_id)
            file_sent = True
        except telegram.error.TimedOut:
            continue

    os.remove(f'downloads/{await music_functions_async.get_name_for_file(full_track)}')
    # скачиваем плейлист
    return ConversationHandler.END


async def start_dialog_making_subscription(update, context):
    """Обработчик первой стадии оформление подписки, начинает диалог"""
    result = music_functions_async.get_id_subscription()
    if update.message.chat_id in result:
        await update.message.reply_text(
            'Вы уже подписаны. Введите "да", если хотите отменить подписку, и "нет" в противном случае. Для выхода из диалога введите /stop',
            reply_markup=markup_search)
    else:
        await update.message.reply_text(
            'Введите "да", если хотите оформить подписки, и "нет" в противном случае. Оформив подписку, вы будете'
            ' ежедневно получать основные изменения в чарте, в дальнейшем, если вы захотите отменить подписку,'
            ' воспользуйтесь этой функцией снова. Для выхода из диалога введите /stop',
            reply_markup=markup_search)
    return 1


async def start_dialog_fast_search_playlists(update, context):
    """Обработчик первой стадии диалога быстрого поиска плейлистов"""
    user_id = music_functions_async.get_user_yandex_login(update.message.chat_id)
    if user_id is None:
        await update.message.reply_text(
            'Вы не зарегистрированы, либо ввели неверный логин при регистрации. Функция недоступна')
    res = await music_functions_async.get_user_playlists(user_id)
    ans = await music_functions_async.process_user_playlist_search(res)
    await update.message.reply_text(ans)
    await update.message.reply_text('Для скачивания плейлиста укажите его номер'
                                    ' в данном списке. Для выхода из диалога введите /stop')
    context.chat_data['user_id'] = user_id
    context.chat_data['playlists_amount'] = len(res)
    context.chat_data['result'] = res
    return 1


async def adding_account(update, context):
    """Обработчик второй стадии диалога, отменяет или оформляет подписку"""
    if update.message.text.lower() != 'да':
        await update.message.reply_text('Сброшено', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    result = music_functions_async.get_id_subscription()
    if update.message.chat_id in result:
        music_functions_async.delete_subscription(update.message.chat_id)
        await update.message.reply_text('подписка успешно отменена',
                                        reply_markup=ReplyKeyboardRemove())
    else:
        music_functions_async.save_subscription(update.message.chat_id, update.message.chat.username)
        await update.message.reply_text('подписка успешно оформлена',
                                        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def register(update, context):
    await update.message.reply_text(
        """Введите логин своего аккаунта Яндекс.Музыки. Для выхода из диалога введите /stop'""")
    return 1


async def get_user_login(update, context):
    login = update.message.text.strip()
    music_functions_async.save_yandex_login(update.message.chat_id, login)
    return ConversationHandler.END


async def get_my_info(update, context):
    res = music_functions_async.get_user_yandex_login(update.message.chat_id)
    if res:
        await update.message.reply_text(f'Ваш логин Яндекс.Музыки: {res}')
    else:
        await update.message.reply_text("Вы еще не зарегистрировались")


async def stop(update, context):
    """Обработчик выхода из диалога"""
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


async def start_dialog_search_random_track(update, context):
    """Начинает диалог поиска случайных треков"""
    await update.message.reply_text('Происходит поиск треков, это может занять пару секунд...')
    receiving = await music_functions_async.search_random_track()
    answer = await music_functions_async.process_search_random_track(receiving)
    await update.message.reply_text(answer)
    await update.message.reply_text(
        'Для скачивания трека введите его номер в этом списке. Для выхода из диалога введите /stop')
    context.chat_data['result'] = receiving
    return 2


async def help_info(update, context):
    await update.message.reply_text("""Как использовать данного бота:
/help - подсказки по командам
···
/stop - используется для выхода из диалогов
···
/search_user_playlists - начать диалог поиска плейлистов пользователя, с возможностью их скачивания
···
/search_track - начать диалог поиска трека, с возможностью его скачивания 
···
/random_track - бот отправит вам совершенно случайную подборку треков
···
/subscription - для оформления и отказа от подписки (вся информация при начале диалога)
···
/register - зарегистрироваться с логином Яндекс.Музыки
···
/playlists - получить список своих плейлистов (своими считаются плейлисты пользователя, логин которого введен при регистрации, для использования требуется зарегистрироваться)
···
/account_info - получить логин, указанный при регистрации""")


async def start(update, context):
    await update.message.reply_text(
        f"Приветсвую тебя {update.message.chat.first_name}. Я музыкальный бот, который работает с Яндекс.Музыкой. Для "
        f"приятной работы со мной, советую воспользоваться функцией /help"
    )


def main():
    # Создаём объект Application.
    application = Application.builder().token(BOT_TOKEN).build()

    # диалог регистрации аккаунта в яндекс музыке
    registration_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('register', register)],
        states={1: [CommandHandler('stop', stop), MessageHandler(filters.ALL, get_user_login)]},
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(registration_conv_handler)

    # диалог быстрого поиска плейлиста
    fast_playlist_search_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('playlists', start_dialog_fast_search_playlists)],
        states={1: [CommandHandler('stop', stop), MessageHandler(filters.ALL, ask_for_playlist_download)],
                3: [CommandHandler('stop', stop), MessageHandler(filters.ALL, download_playlist)]},
        fallbacks=[CommandHandler('stop', stop)])
    application.add_handler(fast_playlist_search_conv_handler)

    # диалог поиска плейлистов
    playlist_search_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('search_user_playlists', start_dialog_search_playlists)],
        states={1: [CommandHandler('stop', stop), MessageHandler(filters.ALL, search_users_playlists)],
                2: [CommandHandler('stop', stop), MessageHandler(filters.ALL, ask_for_playlist_download)],
                3: [CommandHandler('stop', stop), MessageHandler(filters.ALL, download_playlist)]},
        fallbacks=[CommandHandler('stop', stop)])
    application.add_handler(playlist_search_conv_handler)

    # диалог поиска треков
    track_search_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('search_track', start_dialog_search_track)],
        states={1: [CommandHandler('stop', stop), MessageHandler(filters.ALL, search_track)],
                2: [CommandHandler('stop', stop), MessageHandler(filters.ALL, ask_for_track_download)],
                3: [CommandHandler('stop', stop), MessageHandler(filters.ALL, download_track)]},
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(track_search_conv_handler)

    # диалог оформления подписки
    making_subscription = ConversationHandler(
        entry_points=[CommandHandler('subscription', start_dialog_making_subscription)],
        states={1: [CommandHandler('stop', stop), MessageHandler(filters.ALL, adding_account)]},
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(making_subscription)

    # диалог поиска случайных треков
    search_random_track = ConversationHandler(
        entry_points=[CommandHandler('random_track', start_dialog_search_random_track)],
        states={
            2: [CommandHandler('stop', stop), MessageHandler(filters.ALL, ask_for_track_download)],
            3: [CommandHandler('stop', stop), MessageHandler(filters.ALL, download_track)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(search_random_track)

    application.add_handler(CommandHandler('help', help_info))
    application.add_handler(CommandHandler('account_info', get_my_info))
    application.add_handler(CommandHandler('start', start))

    # Запускаем приложение.
    application.run_polling()


reply_keyboard_search = [['Да', 'Нет']]
markup_search = ReplyKeyboardMarkup(reply_keyboard_search, one_time_keyboard=False, resize_keyboard=True)

# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
