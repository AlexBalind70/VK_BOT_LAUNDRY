# -*- coding: utf-8 -*-

import re
import csv
from datetime import date
import requests
import threading

import vk_api
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll


from database_main import *
from keyboard_bot import Menu_Keyboard
from db_position import PositionUser


class Bot_Main(object):
    def __init__(self):
        self.laundry_db = LaundryScheduler()
        self.db_position = PositionUser()
        self.menu_keyboard = Menu_Keyboard()

        token = ""
        self.authorize = vk_api.VkApi(token=token)
        self.vk = self.authorize.get_api()
        self.longpoll = VkLongPoll(self.authorize)

        try:
            for event in self.longpoll.listen():
                if event.type == vk_api.longpoll.VkEventType.MESSAGE_NEW and event.to_me and event.text:
                        self.response = self.vk.users.get(user_ids=event.user_id)
                        self.first_name = self.response[0]['first_name']
                        self.last_name = self.response[0]['last_name']
                        self.db_position.add_new_user(event.user_id)
                        threading.Thread(target=self.processing_message, args=(event.user_id, event.text)).start()
        except ConnectionError or ExceptionGroup:
            pass

    def write_message(self, sender, message, keyboard=None):
        try:
            post = {
                'user_id': sender,
                'message': message,
                'random_id': get_random_id()
            }

            if keyboard is not None:
                post['keyboard'] = keyboard.get_keyboard()

            self.authorize.method('messages.send', post)
        except Exception as e:
            self.sender_chat("Ошибка отправки сообщения у пользователя: \n"
                                          f"\n Имя пользователя: {self.first_name} {self.last_name}"
                                          f"\n Id пользователя: {sender}")
            pass

    def sender_chat(self, message):
        self.authorize.method('messages.send',
                              {'chat_id': 1,
                               'message': message,
                               'random_id': get_random_id()
                               })

    def processing_message(self, sender, received_message):
        number_position = self.db_position.take_position(sender)
        self.laundry_db.scheduler = LaundryScheduler()
        match number_position:
            case "1":
                self.start_menu(sender, received_message)

            case "2":
                if received_message == "Назад в главное меню":
                    self.back_menu(sender)

                elif self.laundry_db.is_valid_date(received_message) and not self.laundry_db.is_past_date(
                        received_message):
                    self.search_date = received_message
                    self.write_message(sender, "Введите временной диапазон (в формате чч:мм-чч:мм):",
                                       self.menu_keyboard.keyboard_menu_time)
                    self.db_position.update_position(sender, "3")

                else:
                    self.write_message(sender,
                                       "Вы ввели некорректную дату или дата уже прошла. "
                                       "Для записи на стирку, введите дату (в формате дд.мм.гггг):")

            case "3":
                if received_message == "Назад в главное меню":
                    self.back_menu(sender)

                elif self.laundry_db.validate_time_format(received_message):
                    self.search_time = received_message
                    self.user_time(sender, self.search_date, self.search_time)

                else:
                    self.write_message(sender, "Вы ввели неверный формат времени. Введите временной диапазон (в формате "
                                               "чч:мм-чч:мм):")

            case "4":
                self.user_room(sender, received_message)

            case "5":
                self.record_confirmation(sender, received_message)

            case "6":
                self.other_peoples_things(sender, received_message)

            case "7":
                self.admin_panel(sender, received_message)

            case "8":
                self.send_file_laundry(sender, received_message)

            case "9":
                self.send_file_ban(sender, received_message)

            case "10":
                self.add_user_ban(sender, received_message)

            case "11":
                self.send_all_user(sender, received_message)

            case "12":
                self.add_admin(sender, received_message)

    def start_menu(self, sender, received_message):
        match received_message:
            case ["Начать", "Меню"]:
                self.write_message(sender,
                                   f"Привет {self.first_name}! \n\nСейчас ты находишься в главном меню. Внизу распалагются кнопки, нажимая на которые ты можешь записать на стирку, узнать правила стирки и",
                                   self.menu_keyboard.keyboard_menu)

            case "Назад в главное меню":
                self.back_menu(sender)

            case "Записаться на стирку":
                ban = self.db_position.take_ban(sender)
                if ban == "0":
                    self.write_message(sender, "Для записи на стирку, введите дату (в формате дд.мм.гггг):")
                    self.db_position.update_position(sender, "2")
                else:
                    self.write_message(sender, "⚠️ На данный момент для вашей комнаты заблокирована стирка! "
                                               "\n\n Если вы считаете, что это ошибка, то обратитесь к Жилищной комиссии РФФ.",
                                       self.menu_keyboard.keyboard_menu)

            case "Правила записи на стирку 📝":
                self.write_message(sender, self.file_messages("static/rools_laundry.txt"), self.menu_keyboard.keyboard_menu)

            case "За что можно получить бан? 🚫":
                self.write_message(sender, self.file_messages("static/ban_files.txt"), self.menu_keyboard.keyboard_menu)

            case "Чужие вещи в машинке":
                self.write_message(sender, "Выберите следующий вариант вашего случая:"
                                           "\n\n1. Машинка выключена, но тут чужие вещи!"
                                           "\n2. В машинке стираются чьи-то вещи, хотя очередь сейчас моя!"
                                           "\n\nОТПРАВЬТЕ МНЕ ВАШ ВАРИАНТ ЦИФРОЙ ИЛИ НАЖМИТЕ НА СООТВЕТСТВУЮЩУЮ КНОПКУ ВНИЗУ❗"
                                   , self.menu_keyboard.keyboard_busy_laundry)
                self.db_position.update_position(sender, 6)

            case "/админ/":
                self.admin(sender)

            case _:
                self.understand_msg(sender)

    def file_messages(self, file_name):
        file_path = f'{file_name}'

        with open(f"{file_path}", "r", encoding="cp1251") as file:
            file_content = file.read()
        return file_content

    def user_time(self, sender, search_date, search_time):

        if self.laundry_db.is_slot_available(search_date, search_time,1) or self.laundry_db.is_slot_available(search_date,search_time, 2):
            self.db_position.update_position(sender, "4")
            self.write_message(sender, "Введите номер вашей комнаты:")

        else:
            available_dates = self.laundry_db.find_available_slots(search_date, search_time)
            message = "К сожалению выбранная дата и время заняты.\n\n" \
                            f"Но выбранный вами период стирки ({search_time}) свободен в следующие дни:\n\n"

            for i, date in enumerate(available_dates):
                message += f"{i + 1}. {date}\n"
            message += "\nВозвращаю вас в главное меню!"
            self.write_message(sender, message, self.menu_keyboard.keyboard_menu)
            self.db_position.update_position(sender, 1)


    def data_verification(self, sender, search_date, search_time, value_room):
        if not self.laundry_db.check_weekly_limit(value_room, search_date):
            self.write_message(sender, "Перед записью давайте "
                                    "сверим информацию.\n"
                                    f"\nДата записи на стирку: {search_date}"
                                    f"\nВремя стирки: {search_time}"
                                    f"\nНомер комнаты: {value_room}\n\n"
                                    )
            self.db_position.update_position(sender, "5")
            self.write_message(sender, f"Для подтверждения записи "
                                        f"отправьте сообщение "
                                        f"Да/Нет или нажмите на "
                                        f"кнопку, "
                                        f"которая располагается "
                                        f"внизу.", self.menu_keyboard.keyboard_confirmation)

        else:
            self.write_message(sender,"Лимит стирок для вашей комнаты на этой недели исчерпан. Если вы "
                                "считаете, что это ошибка, то обратитесь к Жилищной комиссии РФФ.",
                                self.menu_keyboard.keyboard_menu)
            self.sender_chat("⚠️⚠️⚠️ - Исчерпан лимит"
                                f"\nКоманата - {value_room}"
                                f"\nПользователь - {sender} ({self.first_name} {self.last_name})"
                                )

            self.db_position.update_position(sender, "1")

    def user_room(self, sender, received_message):
            if received_message == "Назад в главное меню":
                self.back_menu(sender)

            elif self.laundry_db.is_valid_number(received_message):
                self.value_room = received_message
                self.db_position.update_room(sender, self.value_room)
                self.user_real_room = self.db_position.take_room(sender)
                if self.value_room == self.user_real_room:
                    self.data_verification(sender, self.search_date, self.search_time, self.value_room)

                else:
                    self.write_message(sender, f"Вы ввели неверную комнату. Вы живёте в {self.user_real_room} комнате. "
                                               f"Если считаете это ошибкой, свяжитесь с Жилищной комиссией РФФ."
                                               f"\n\nОТПРАВЬТЕ, ПОЖАЛУЙСТА, НОМЕР СВОЕЙ КОМНАТЫ.", self.menu_keyboard.keyboard_back_menu)

            else:
                self.write_message(sender,
                                   "Вы ввели не коректный номер комнаты или ваша комната, не относится к "
                                   "Радиофизическому факультету. Если вы считаете по другому, то обратитесь к "
                                   "Жилищной комиссии РФФ."
                                   "\n\n Отправьте верный номер своей комнаты!")

    def record_confirmation(self, sender, received_message):
        if received_message == "Да":
            self.make_reservation(sender, self.search_date, self.search_time, self.value_room)
        elif received_message == "Нет":
            self.write_message(sender, "Вы отменили запись, возвращаю вас в главное меню. ",
                               self.menu_keyboard.keyboard_menu)
            self.db_position.update_position(sender, "1")
        else:
            self.write_message(sender, "Ожидаю подтверждения записи...")

    def make_reservation(self, sender, search_date, search_time, value_room):

        try:
            cursor = self.laundry_db.conn.cursor()
            cursor.execute("BEGIN")  # Начать транзакцию
            if self.laundry_db.is_slot_available(search_date, search_time, 1):
                # Забронировать слот и подтвердить транзакцию
                self.reserve_slot(cursor, value_room, search_date, search_time, slot_number=1)
                self.laundry_db.conn.commit()
                self.write_message(sender, "Вы успешно записаны на стирку."
                                                f"\n\nДата: {search_date}"
                                                f"\nВремя: {search_time}"
                                                f"\nСтиральная машинка: 1-я от окна",
                                                self.menu_keyboard.keyboard_menu)
                self.sender_chat("👤👤👤"
                                f"\nИмя пользователя: {self.first_name} {self.last_name}"
                                f"\nId пользователя: {sender} "
                                f"\nЗаписался на 1-ую машинку."
                                f"\nДата: {search_date}"
                                f"\nВремя: {search_time}"
                                )
                self.db_position.update_position(sender, "1")

            elif self.laundry_db.is_slot_available(search_date, search_time, 2):
                # Забронировать слот и подтвердить транзакцию
                self.reserve_slot(cursor, value_room, search_date, search_time, slot_number=2)
                self.laundry_db.conn.commit()
                self.write_message(sender, "Вы успешно записаны на стирку."
                                            f"\n\nДата: {search_date}"
                                            f"\nВремя: {search_time}"
                                            f"\nСтиральная машинка: 2-я от окна",
                                    self.menu_keyboard.keyboard_menu)
                self.sender_chat("👤👤👤"
                                f"\nИмя пользователя: {self.first_name} {self.last_name}"
                                f"\nId пользователя: {sender}"
                                f"\nЗаписался на 2-ую машинку."
                                f"\nДата: {search_date}"
                                f"\nВремя: {search_time}"
                                )
                self.db_position.update_position(sender, "1")
            else:
                self.laundry_db.conn.rollback()  # Откатить транзакцию
                self.write_message(sender, "Вас успели опередили - это время уже заняли."
                                            "\nВозвращаю вас в главное меню.", self.menu_keyboard.keyboard_menu)
                self.sender_chat("⚠️⚠️⚠️"
                                f"\nИмя пользователя: {self.first_name} {self.last_name}"
                                f"\nId пользователя: {sender}"
                                f"Не смог записаться, так как его опередили.")
                self.db_position.update_position(sender, "1")
        except Exception as e:
            self.laundry_db.conn.rollback()  # Откатить транзакцию при ошибке
            self.sender_chat(f"‼️️‼️‼️"
                            f"\nПроизошла ошибка при записи на стирку у пользователя {sender} ({self.first_name} {self.last_name}).")


    def reserve_slot(self, cursor, room_number, date, time, slot_number):
                # Обновить указанный слот номером комнаты пользователя
            cursor.execute(
                    f"UPDATE laundry SET slot{slot_number} = %s WHERE date = %s AND time = %s "
                    f"AND (slot{slot_number} IS NULL OR slot{slot_number} = 'Свободно')",
                    (room_number, date, time)
            )

    def other_peoples_things(self, sender, received_message):
        answer = received_message
        if answer in ["Машинка выключена, но тут чужие вещи!", "1"]:
            self.write_message(sender, "Если настало время вашей стирки, а в машинке оказались чьи-то вещи, "
                                       "просто переложите их на подоконник/машинку/пол/в окно 🧐", self.menu_keyboard.keyboard_menu)
            self.sender_chat("‼️⚠️‼️️ - Чужие вещи в машинке"
                             f"\nИмя пользователя: {self.first_name} {self.last_name}"
                             f"\nId пользователя: {sender}"
                             f"\nЧужие вещи в машинке! Обратить внимание‼️")
            self.db_position.update_position(sender, 1)
        elif answer in ['В машинке стираются чьи-то вещи!', '2']:
            self.write_message(sender, "Напишите, пожалуйста об этом любому следующему человеку из Жилищной комисии РФФ:"
                                       "\n\n@vestlag (Иван Гальцев) - предсидатель ЖК РФФ"
                                       "\n@alexandr_rff (Александр Щербаков) - расселитель"
                                       "\n@s.mashkov00 (Сергей Машков) - староста 5 этажа"
                                       "\n@id670480584 (Никита Терещенко) - староста 6 этажа", self.menu_keyboard.keyboard_menu)
            self.sender_chat("️‼️‼️️‼️️ - Чужой"
                             f"\nИмя пользователя: {self.first_name} {self.last_name}"
                             f"\nId пользователя: {sender}"
                             f"\nКто стирается не в свое время. Обратить внимание‼️")
            self.db_position.update_position(sender, 1)

        elif answer == "Назад в главное меню":
            self.back_menu(sender)

        else:
            self.write_message(sender, "Опишите, пожалуйста, вашу проблему! Пока, я вас не понимаю.", self.menu_keyboard.keyboard_busy_laundry)

    def admin(self, sender):
        if self.read_admin(sender) == True:
            self.db_position.update_position(sender, 7)
            self.sender_chat(f"👤👤👤 - Админка"
                             f"\nИмя пользователя: {self.first_name} {self.last_name}"
                             f"\nId пользователя: {sender}")

            self.write_message(sender, f"{self.first_name}, добро пожаловать в панель администратора!\n"
                                       "\n⚠️Будьте осторожны с рассылкой⚠️", self.menu_keyboard.keyboard_admin)
        else:
            self.understand_msg(sender)

    def admin_panel(self, sender, received_message):
        if received_message == "Выгрузка записей на стирку":
            self.write_message(sender, "Напишите диапозон дат для выгрузки в формате 01.01.2023 - 30.01.2023")
            self.db_position.update_position(sender, 8)

        elif received_message == "Выгрузка нарушителей правил стирки":
            self.write_message(sender, "Выгружаю список нарушителей правил...")
            self.db_position.update_position(sender, 9 )

        elif received_message == "Добавить нарушителя правил":
            self.write_message(sender, "Отправьте ссылку на нарушителя в формате:"
                                       "\nhttps://vk.com/raccoon_balind")
            self.db_position.update_position(sender, 10)

        elif received_message == "Сделать рассылку всем пользователям":
            self.write_message(sender, "Скоро добавим")

        elif received_message == "Добавить администратора":
            if sender == 290565131:
                self.write_message(sender, "Отправьте ссылку пользователя для добавления администратора в формате:"
                                           "\n https://vk.com/raccoon_balind")
                self.db_position.update_position(sender, 12)

            else:
                self.write_message(sender, "У вас не прав для добавления админов! Приказ Енота.")

        elif received_message == "Вернуться в обычное меню":
            self.write_message(sender, "Возвращаю вас в обычное меню", self.menu_keyboard.keyboard_menu)
            self.db_position.update_position(sender, 1)

    def send_file_laundry(self, sender, received_message):
        pattern = r'(\d{2}\.\d{2}\.\d{4}) - (\d{2}\.\d{2}\.\d{4})'
        match = re.match(pattern, received_message)
        start_date_str = match.group(1)
        end_date_str = match.group(2)

        start_date_components = start_date_str.split('.')
        end_date_components = end_date_str.split('.')

        start_date = date(int(start_date_components[2]), int(start_date_components[1]), int(start_date_components[0]))
        end_date = date(int(end_date_components[2]), int(end_date_components[1]), int(end_date_components[0]))
        data_from_db = self.laundry_db.get_laundry_values(start_date, end_date)

        if data_from_db:
            file_path = 'output.csv'
            with open(file_path, 'w+', encoding='cp1251', newline='') as csvfile:  # Используем codecs.open
                writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL, delimiter=',', lineterminator='\n')

                writer.writerow(['date', 'time', 'slot1', 'slot2'])
                for row in data_from_db:
                    writer.writerow(row)

            self.send_to_admin(sender)

        else:
            self.write_message(sender, 'Не удалось выгрузить данные и сохранить!')

        self.db_position.update_position(sender, 7)

    def send_to_admin(self, sender):
        upload_url = self.get_upload_url(self.vk, sender)
        file_path = 'output.csv'
        upload_response = self.upload_file(upload_url, file_path)

        doc_id, owner_id = self.save_file(self.vk, upload_response['file'])
        self.send_file(self.vk, sender, doc_id, owner_id)

    def get_upload_url(self, vk, sender):
        response = vk.docs.getMessagesUploadServer(type='doc', peer_id=sender)
        upload_url = response['upload_url']

        return upload_url

    def upload_file(self, upload_url, file_path):
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(upload_url, files=files)
        return response.json()

    def save_file(self, vk, file):
        response = vk.docs.save(file=file)
        doc_id = response['doc']['id']
        owner_id = response['doc']['owner_id']
        return doc_id, owner_id

    def send_file(self, vk, sender, doc_id, owner_id):
        attachment = f"doc{owner_id}_{doc_id}"
        vk.messages.send(user_id=sender, message='Вот файл с данными о записях на стирке', attachment=attachment, random_id=0)
        self.write_message(sender, 'Возвращаю вас ', self.menu_keyboard.keyboard_admin)

    def add_user_ban(self, sender, received_message):
        id_ban = self.url_to_iduser(received_message)
        self.db_position.update_ban(id_ban, 1)
        self.write_message(sender, 'Пользователь добавлен в чёрный список!', self.menu_keyboard.keyboard_admin)
        self.db_position.update_position(sender, 7)

    def url_to_iduser(self, url):
        screen_name = url.split('/')[-1]
        id_ = self.authorize.method('users.get', {'user_ids': screen_name})[0]['id']
        return id_

    def read_admin(self, sender):
        with open("static/admin_profiles.txt", 'r') as file:
            existing_profiles = file.read().splitlines()

            if f"{sender}" in existing_profiles:
                return True

    def save_admin_profile(self, user_id):
        self.response = self.vk.users.get(user_ids=user_id)

        with open("static/admin_profiles.txt", "a+") as file:
            file.seek(0)
            existing_profiles = file.read().splitlines()

            if f"{user_id}" not in existing_profiles:
                file.write(f"{user_id}\n")

    def add_admin(self,sender, received_message):
        url = received_message
        try:
            id_admin = self.url_to_iduser(url)
            self.save_admin_profile(id_admin)
            self.write_message(sender, "Админ добавлен!", self.menu_keyboard.keyboard_admin)
            self.sender_chat("👤👤👤 - Админка"
                             f"\nИмя пользователя: {self.first_name} {self.last_name}"
                             f"\nId пользователя: {sender}"
                             f"\nДобавил админа - {id_admin}")
        except Exception as ex:
            self.sender_chat("👤👤👤 - Админка"
                             f"\nИмя пользователя: {self.first_name} {self.last_name}"
                             f"\nId пользователя: {sender}"
                             f"\nОшибка: {ex}")
        self.db_position.update_position(sender, 1)

    def understand_msg(self, sender):
        self.write_message(sender, "Не понял ваше сообщение.", self.menu_keyboard.keyboard_menu)

    def back_menu(self, sender):
        self.write_message(sender, f" {self.first_name}, вы вернулись в главное меню", self.menu_keyboard.keyboard_menu)
        self.db_position.update_position(sender, 1)

    def send_all_user(self, sender, received_message):
        self.write_message(sender, "Скоро добавим", self.menu_keyboard.keyboard_admin)
        self.db_position.update_position(sender, 7)

    def send_file_ban(self, sender, received_message):
        self.write_message(sender, "Скоро добавим", self.menu_keyboard.keyboard_admin)
        self.db_position.update_position(sender, 7)

