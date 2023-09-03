# -*- coding: utf-8 -*-

from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class Menu_Keyboard(object):
    def __init__(self):
        settings = dict(one_time=True)
        settings_time = dict(one_time=True)

        self.keyboard_menu = VkKeyboard(**settings)
        self.keyboard_menu.add_button('Записаться на стирку', color=VkKeyboardColor.POSITIVE)
        self.keyboard_menu.add_line()
        self.keyboard_menu.add_button('Правила записи на стирку 📝', color=VkKeyboardColor.SECONDARY)
        self.keyboard_menu.add_line()
        self.keyboard_menu.add_button('За что можно получить бан? 🚫', color=VkKeyboardColor.SECONDARY)
        self.keyboard_menu.add_line()
        self.keyboard_menu.add_button('Чужие вещи в машинке', color=VkKeyboardColor.SECONDARY)

        self.keyboard_menu_time = VkKeyboard(**settings_time)
        self.keyboard_menu_time.add_button("9:00-11:00", color=VkKeyboardColor.SECONDARY)
        self.keyboard_menu_time.add_line()
        self.keyboard_menu_time.add_button("12:00-14:00", color=VkKeyboardColor.SECONDARY)
        self.keyboard_menu_time.add_line()
        self.keyboard_menu_time.add_button("15:00-17:00", color=VkKeyboardColor.SECONDARY)
        self.keyboard_menu_time.add_line()
        self.keyboard_menu_time.add_button("18:00-20:00", color=VkKeyboardColor.SECONDARY)
        self.keyboard_menu_time.add_line()
        self.keyboard_menu_time.add_button("21:00-23:00", color=VkKeyboardColor.SECONDARY)
        self.keyboard_menu_time.add_line()
        self.keyboard_menu_time.add_button("Назад в главное меню", color=VkKeyboardColor.NEGATIVE)

        self.keyboard_busy_laundry = VkKeyboard(**settings_time)
        self.keyboard_busy_laundry.add_button("Машинка выключена, но тут чужие вещи!", color=VkKeyboardColor.SECONDARY)
        self.keyboard_busy_laundry.add_line()
        self.keyboard_busy_laundry.add_button("В машинке стираются чьи-то вещи!", color=VkKeyboardColor.SECONDARY)
        self.keyboard_busy_laundry.add_line()
        self.keyboard_busy_laundry.add_button("Назад в главное меню", color=VkKeyboardColor.NEGATIVE)

        self.keyboard_admin = VkKeyboard(**settings)
        self.keyboard_admin.add_button("Выгрузка записей на стирку", color=VkKeyboardColor.POSITIVE)
        self.keyboard_admin.add_line()
        self.keyboard_admin.add_button("Выгрузка нарушителей правил стирки")
        self.keyboard_admin.add_line()
        self.keyboard_admin.add_button("Добавить нарушителя правил")
        self.keyboard_admin.add_line()
        self.keyboard_admin.add_button("Сделать рассылку всем пользователям", color=VkKeyboardColor.SECONDARY)
        self.keyboard_admin.add_line()
        self.keyboard_admin.add_button("Добавить администратора", color=VkKeyboardColor.SECONDARY)
        self.keyboard_admin.add_line()
        self.keyboard_admin.add_button("Вернуться в обычное меню", color=VkKeyboardColor.NEGATIVE)

        self.keyboard_back_menu = VkKeyboard(**settings)
        self.keyboard_back_menu.add_button("Назад в главное меню", color=VkKeyboardColor.NEGATIVE)

        self.keyboard_confirmation = VkKeyboard(**settings_time)
        self.keyboard_confirmation.add_button("Да", VkKeyboardColor.POSITIVE)
        self.keyboard_confirmation.add_button("Нет", VkKeyboardColor.SECONDARY)
