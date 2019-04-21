import threading

import pyrogram

import time

import schedule

import json


class ChatCleanerBot(threading.Thread):
    def __init__(self, app: pyrogram.Client):
        super().__init__()
        self.app = app

    def run(self):
        self.__subscribe__()
        schedule.every().day.at('00:00').do(self.__exec__)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def __exec__(self):
        groups = ChatCleanerBot.__get_groups__()
        for chat in groups:
            if not self.__update_group__(chat):
                continue
            members_count = self.app.get_chat_members_count(chat)
            members = []
            while len(members) < members_count:
                members.extend(self.app.get_chat_members(chat, len(members), 200).chat_members)
            deleted_count = 0
            for member in members:
                if member.user.is_deleted:
                    deleted_count += 1
                    self.app.kick_chat_member(chat, member.user.id)
            self.__send__(chat, '‼️ ' + str(deleted_count) + ' dead souls were removed.')

    def __check_permissions__(self, chat_id: str) -> bool:
        me = self.app.get_me()
        try:
            user = self.app.get_chat_member(chat_id, me.id)
        except Exception as e:
            print(e)
            return False
        return user.status == 'administrator' and user.permissions.can_restrict_members

    def __subscribe__(self):
        @self.app.on_message()
        def on_message(client, message: pyrogram.Message):
            self.__update_group__(message.chat.id)

    def __update_group__(self, chat: str) -> bool:
        groups = ChatCleanerBot.__get_groups__()
        if groups.count(chat) == 0 and self.__check_permissions__(chat):
            groups.append(chat)
            self.__send__(chat, 'Group was added to cleaner list')
        elif groups.count(chat) == 1 and not self.__check_permissions__(chat):
            groups.remove(chat)
            self.__send__(chat, 'Group was removed from cleaner list')
        ChatCleanerBot.__set_groups__(groups)
        return groups.count(chat) == 1

    def __send__(self, chat: str, text: str):
        try:
            self.app.send_message(chat, text)
        except Exception as e:
            print(e)

    @staticmethod
    def __get_groups__():
        try:
            groups = json.load(open('./groups.json', 'r'))
        except FileNotFoundError:
            groups = []
        return groups

    @staticmethod
    def __set_groups__(groups: list):
        json.dump(groups, open('./groups.json', 'w'))


