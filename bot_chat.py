# -*- coding: utf-8 -*-

import re
import time
import threading

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from db_position import PositionUser

class Chat_Bot:
    def __init__(self):
        self.position = PositionUser()

        group_token = ""
        self.group_session = vk_api.VkApi(token=group_token)
        group_api = self.group_session.get_api()

        longpoll_chat = VkBotLongPoll(self.group_session, group_id="")

        for event in longpoll_chat.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat and event.message.get('text') != "":
                message_chat = event.message.get('text')
                chat = event.chat_id
                self.process_message(chat, message_chat)
                pass

    def sender_chat(self,chat, message):
        self.group_session.method('messages.send',
                                { 'chat_id': chat,
                               'message': message,
                               'random_id': 0 })

    def process_message(self, chat, received_message):
        if '/position ' in received_message:
            self.position_update(chat, received_message)

        elif '/check_position' in received_message:
            self.check_position(chat, received_message)

        elif '/update_room' in received_message:
            self.update_room(chat, received_message)

        elif '/take_room' in received_message:
            self.take_room(chat, received_message)

        elif '/ban' in received_message:
            self.ban_update(chat, received_message)

        else:
            pass

    def position_update(self, chat, received_message):
        try:
            pattern = r'/position (\d+) (\d+)'
            match = re.match(pattern, received_message)
            user_id = match.group(1)
            position_number = match.group(2)

            if self.position.user_exists(user_id):
                self.position.update_position(user_id, position_number)
                self.sender_chat(chat, "🤘 Успешно изменил позицию пользователя")
            else:
                self.sender_chat(chat, f"⚠️Не удалось изменить позицию пользователя - {user_id}")
        except Exception as ex:
            self.sender_chat(chat, f"⚠️ERROR - {ex}")

    def check_position(self,chat, received_message):
        pattern = r'/check_position (\d+)'
        try:
            match = re.match(pattern, received_message)
            user_id = match.group(1)
            self.sender_chat(chat,f'🤘 Позиция пользователя - {self.position.take_position(user_id)}')
        except Exception as ex:
            self.sender_chat(chat, f"⚠️ERROR - {ex}")

    def update_room(self, chat, received_message):
        pattern = r'/update_room (\d+) (\d+)'
        try:
            match = re.match(pattern, received_message)
            user_id = match.group(1)
            room = match.group(2)
            self.position.change_room(user_id, room)
            self.sender_chat(chat, f"🤘 Успешно изменил комнату у пользователя!")
        except Exception as ex:
            self.sender_chat(chat, f"⚠️ERROR - {ex}")

    def take_room(self, chat, received_message):
        pattern = r'/take_room (\d+)'
        try:
            match = re.match(pattern, received_message)
            user_id = match.group(1)
            room = self.position.take_room(user_id)
            self.sender_chat(chat, f"🤘 Комната пользователя {user_id} - {room}")
        except Exception as ex:
            self.sender_chat(chat, f"⚠️ERROR - {ex}")

    def ban_update(self, chat, received_message):
        pattern = r'/ban (\d+)'
        try:
            match = re.match(pattern, received_message)
            user_id = match.group(1)
            room = self.position.update_ban(user_id, 0)
            self.sender_chat(chat, f"🤘 Пользователь разблокирован успешно {user_id} - {room}")
        except Exception as ex:
            self.sender_chat(chat, f"⚠️ERROR - {ex}")





