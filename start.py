import pyrogram

import conf

import main

app = pyrogram.Client(
    "chat_cleaner_bot",
    **conf.api,
    bot_token=conf.bot_token
)

main.ChatCleanerBot(app).start()

app.run()
