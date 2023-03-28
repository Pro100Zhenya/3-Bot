# Импортируем необходимые классы.
import logging
import os

import telegram.error
import yandex_music.exceptions
from telegram.ext import Application, MessageHandler, filters, ConversationHandler

import music_functions_async
from Token import BOT_TOKEN
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup,InputMediaPhoto,MenuButtonCommands,MenuButton,ReplyKeyboardRemove,MenuButtonWebApp,\
    InlineKeyboardButton, InlineKeyboardMarkup, MenuButton
# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

# Определяем функцию-обработчик сообщений.
# У неё два параметра, updater, принявший сообщение и контекст - дополнительная информация о сообщении.

# Напишем соответствующие функции.
# Их сигнатура и поведение аналогичны обработчикам текстовых сообщений.

# async def start(update, context):
#     """Отправляет сообщение когда получена команда /start"""
#     user = update.effective_user
#     await update.message.reply_html(
#         rf"Привет {user.mention_html()}! Я поисковая машина. Напишите мне что-нибудь, и я все сделаю, хозяин!",
#     )
#
#
# async def help_command(update, context):
#     """Отправляет сообщение когда получена команда /help"""
#     await update.message.reply_text("Этот умеет искать, сранивать и сохранять товары) А кирилл лох")
#
#
# async def favourites_command(update, context):
#     """Отправляет сообщение когда получена команда /help"""
#     await update.message.reply_text("Ничерта")
#
#
# async def search_command(update, context):
#     """Отправляет сообщение когда получена команда /help"""
#     static_api_request = f"https://yandex.ru/images/search?pos=0&text=%D0%BA%D0%B0%D1%80%D1%82%D0%B8%D0%BD%D0%BA%D0%B0%20%D0%BD%D0%BE%D0%B6%D0%B0%20%D0%B4%D0%BB%D1%8F%20%D0%B8%D0%B3%D1%80&img_url=http%3A%2F%2Fw7.pngwing.com%2Fpngs%2F518%2F558%2Fpng-transparent-hunting-survival-knives-bowie-knife-utility-knives-weapon-knife-angle-arm-weapon.png&source=serp&rpt=simage&lr=53"
#     medias = [InputMediaPhoto(static_api_request),
#               InputMediaPhoto(static_api_request)]
#     await context.bot.send_media_group(
#         update.message.chat_id,  # Идентификатор чата. Куда посылать картинку.
#         # Ссылка на static API, по сути, ссылка на картинку.
#         # Телеграму можно передать прямо её![](knife_6_01153805.jpg), не скачивая предварительно карту.
#         medias, caption='''Нож питерский\nfgfgfg\nfgfgf😘'''
#     )
#     await update.message.reply_photo('knife_6_01153805.jpg', caption='''Нож питерский\nfgfgfg\nfgfgf😘''')
#     await update.message.reply_text('knife_6_01153805.jpg')
#
#
# async def photo_command(update, context):
#     pass
#
#
# async def echo(update, context):
#     if (update.message.text).split()[0]=='Поиск:':
#         static_api_request = (update.message.text).split()[1]
#         medias = [InputMediaPhoto(static_api_request),
#                   InputMediaPhoto(static_api_request)]
#         await context.bot.send_media_group(
#             update.message.chat_id,  # Идентификатор чата. Куда посылать картинку.
#             # Ссылка на static API, по сути, ссылка на картинку.
#             # Телеграму можно передать прямо её![](knife_6_01153805.jpg), не скачивая предварительно карту.
#             medias, caption='''...
# Первый товар
# Цена: 250р
# Отзывы: ⭐⭐⭐⭐
# Ссылка для покупки: url.fgsjjhd
# ...
# Второй товар
# Цена: 250р
# Отзывы: ⭐⭐⭐⭐
# Ссылка для покупки: url.fgsjjhd
# ...
# Третий товар
# Цена: 250р
# Отзывы: ⭐⭐⭐⭐
# Ссылка для покупки: url.fgsjjhd
# ...'''
#         )
#     else:
#         await update.message.reply_text(update.message.text)


# async def search_track(update, context):
#     search_string = update.message.text[13:].strip()  # 12 - длина команды
#     search_result = await music_functions_async.search(search_string)
#     answer = await music_functions_async.process_search(search_result)
#     await update.message.reply_text(answer)


async def search_users_playlists(update, context):
    """Обработчик первой стадии диалога поиска плейлистов, выполняет поиск по id"""
    user_id = update.message.text[len('search_user_playlists') + 2:]
    # print(user_id)
    res = await music_functions_async.get_user_playlists(user_id)
    ans = await music_functions_async.process_user_playlist_search(res)
    await update.message.reply_text(ans)
    await update.message.reply_text('Для скачивания плейлиста укажите его номер'
                                    ' в данном списке, для выхода введите /stop')
    context.chat_data['user_id'] = user_id
    context.chat_data['playlists_amount'] = len(res)
    context.chat_data['result'] = res
    return 1


async def ask_for_playlist_download(update, context):
    """Обработчик второй стадии диалога поиска плейлистов, получение номера требуемого плейлиста"""
    try:
        num = int(update.message.text)
        # print(num, 'введено')
    except ValueError:
        await update.message.reply_text('Введен неверный номер, попробуйте снова')
        return 1
    if num > context.chat_data['playlists_amount']:
        await update.message.reply_text('Введен слишком большой номер, попробуйте снова')
        return 1
    await update.message.reply_text(f'Вы точно хотите скачать плейлист\n '
                                    f'{await music_functions_async.get_playlist_name(context.chat_data["result"][num - 1])}?\n'
                                    f'Введите да, если хотите скачать плейлист, и любой другой ответ в ином случае')
    context.chat_data['num'] = num
    return 2


async def download_playlist(update, context):
    """Обработчик третьей стадии диалога поиска плейлистов, скачивание плейлиста"""
    if update.message.text.lower() != 'да':
        await update.message.reply_text('Скачивание отменено')
        return ConversationHandler.END
    await update.message.reply_text('Скачиваем...')
    playlist = context.chat_data['result'][context.chat_data['num'] - 1]
    # for track in await playlist.fetch_tracks_async():
    for track in (await music_functions_async.client.users_playlists(playlist.kind, playlist.owner.uid)).tracks:
        full_track = await track.fetch_track_async()
        await music_functions_async.download(full_track, folder='downloads/')
        await update.message.reply_text(f'{full_track["title"]} отправляется...')
        file_sent = False
        while not file_sent:
            try:
                await context.bot.send_document(
                    document=open(f'downloads/{await music_functions_async.get_name_for_file(full_track)}', 'rb'), chat_id=update.message.chat_id)
                file_sent = True
            except telegram.error.TimedOut:
                continue

        os.remove(f'downloads/{await music_functions_async.get_name_for_file(full_track)}')
    # скачиваем плейлист
    return ConversationHandler.END


async def search_track_start(update, context):
    """Обработчик первой стадии диалога поиска треков, выполняет поиск"""
    search_string = update.message.text[13:].strip()  # 12 - длина команды
    search_result = await music_functions_async.search(search_string)
    answer = await music_functions_async.process_search(search_result)
    await update.message.reply_text(answer)
    await update.message.reply_text('Для скачивания трека введите его номер в этом списке, для отмены введите /stop')
    context.chat_data['result'] = search_result['tracks']['results']
    return 1


async def ask_for_track_download(update, context):
    """Обработчик второй стадии поиска треков, отвечает за получение номера скачиваемого трека"""
    try:
        num = int(update.message.text)
        # print(num, 'введено')
    except ValueError:
        await update.message.reply_text('Введен неверный номер, попробуйте снова')
        return 1
    if num > 10:
        await update.message.reply_text('Введен слишком большой номер, попробуйте снова')
        return 1
    await update.message.reply_text(f'Вы точно хотите скачать трек\n '
                                    f'{await music_functions_async.get_track_name(context.chat_data["result"][num - 1])}?\n'
                                    f'Введите да, если хотите скачать трек, и любой другой ответ в ином случае')
    context.chat_data['num'] = num
    return 2


async def download_track(update, context):
    """Обработчик третьей стадии диалога поиска треков, скачивание трека"""
    if update.message.text.lower() != 'да':
        await update.message.reply_text('Скачивание отменено')
        return ConversationHandler.END
    await update.message.reply_text('Скачиваем...')
    full_track = context.chat_data['result'][context.chat_data['num'] - 1]
    await music_functions_async.download(full_track, folder='downloads/')
    await update.message.reply_text(f'{await music_functions_async.get_track_name(full_track)} отправляется...')
    file_sent = False
    while not file_sent:
        try:
            await context.bot.send_document(
                    document=open(f'downloads/{await music_functions_async.get_name_for_file(full_track)}', 'rb'), chat_id=update.message.chat_id)
            file_sent = True
        except telegram.error.TimedOut:
            continue

    os.remove(f'downloads/{await music_functions_async.get_name_for_file(full_track)}')
    # скачиваем плейлист
    return ConversationHandler.END


async def stop(update, context):
    """Обработчик выхода из диалога"""
    await update.message.reply_text("Всего доброго!")
    return ConversationHandler.END


def main():
    # Создаём объект Application.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    application = Application.builder().token(BOT_TOKEN).build()

    # text_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)

    # Регистрируем обработчик в приложении.
    # application.add_handler(text_handler)
    # application.add_handler(CommandHandler("start", start))
    # application.add_handler(CommandHandler("help", help_command))
    # application.add_handler(CommandHandler("favourites", favourites_command))
    # application.add_handler(CommandHandler("search", search_command))


    playlist_search_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('search_user_playlists', search_users_playlists)],
        states={1: [CommandHandler('stop', stop), MessageHandler(filters.ALL, ask_for_playlist_download)],
                2: [CommandHandler('stop', stop), MessageHandler(filters.ALL, download_playlist)]},
        fallbacks=[CommandHandler('stop', stop)])
    application.add_handler(playlist_search_conv_handler)

    track_search_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('search_track', search_track_start)],
        states={1: [CommandHandler('stop', stop), MessageHandler(filters.ALL, ask_for_track_download)],
                2: [CommandHandler('stop', stop), MessageHandler(filters.ALL, download_track)]},
        fallbacks=[CommandHandler('stop', stop)]
    )
    application.add_handler(track_search_conv_handler)
    # Запускаем приложение.
    application.run_polling()


async def start(update, context):
    await update.message.reply_text(
        "Я бот-справочник. Какая информация вам нужна?",
    )


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()