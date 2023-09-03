# -*- coding: utf-8 -*-

import time
import threading
from bot_chat import Chat_Bot
from bot import Bot_Main


def main():
    try:
        Bot_Main()
    except Exception as eror:
        print(eror)
        time.sleep(10)
        pass


def chat_bot_thread():
    try:
        Chat_Bot()
    except Exception as eror:
        print(eror)
        time.sleep(10)
        pass


if __name__ == "__main__":
    chat_bot_thread = threading.Thread(target=chat_bot_thread)
    chat_bot_thread.start()
    main()
