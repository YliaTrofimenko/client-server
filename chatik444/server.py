import threading, socket, pickle, base64, time, uuid, os, logging
import os.path
from os import path
from datetime import datetime
from gui_helper import *
from model import *
from utils import *


class Server:

    '''
        ИНИЦИАЛИЗАЦИЯ ГРАФИЧЕСКОГО ИНТЕРФЕЙСА СЕРВЕРА
    '''
    def __init__(self):
        # создание и настройка окна
        self.gui_helper = GUIHelper()
        self.window = self.gui_helper.window_build(self._close_callback)

        # инициализирует некоторые атрибуты
        self.clients = []
        self.logins = []
        self.the_file = []

        # метод построения элементов экрана
        self._build()


    '''
        ВЫЗЫВАЕТ МЕТОДЫ, КОТОРЫЕ СТРОЯТ ЭЛЕМЕНТЫ ЭКРАНА
    '''
    def _build(self):
        self._build_message_area()
        self._build_connecteds_area()


    '''
        СОЗДАЕТ ОБЛАСТЬ ЛОГОВ
    '''
    def _build_message_area(self):
        self.f_messages = self.gui_helper.message_area_build(self.window, 'Логи сервера', height=28)


    '''
        СОЗДАЕТ ЗОНУ ПОДКЛЮЧЕННЫХ ПОЛЬЗОВАТЕЛЕЙ
    '''
    def _build_connecteds_area(self):
        self.f_connecteds = self.gui_helper.connecteds_area_build(self.window, 'Участники', height=27)


    '''
        ОТОБРАЖЕНИЕ ЛОГОВ НА ЭКРАНЕ
    '''
    def _show_message_on_screen(self, message):
        self.gui_helper.update_message_area(self.f_messages, message)


    '''
        ОТОБРАЖЕНИЕ ВОШЕДШИХ ПОЛЬЗОВАТЕЛЕЙ НА ЭКРАНЕ
    '''
    def _update_users_on_screen(self):
        self.f_connecteds.delete(0,END)
        i = 0
        for user in self.logins:
            self.f_connecteds.insert(i, user)
            i = i + 1


    '''
        УВЕДОМЛЯЕТ УЧАСТНИКОВ НОВЫМ СООБЩЕНИЕМ
    '''
    def broadcast(self, current_client, message):
        recipient = self.get_recipient(message)
        if recipient != None:

            if current_client != recipient:
                send_serialized(recipient, message)

                # клиент, отправивший изображение, не должен его получать
                if message.command != 'REQUEST_PATH':
                    send_serialized(current_client, message)
        else:

            for client in self.clients:

                if message.command == 'REQUEST_PATH':
                    if client != current_client:
                        send_serialized(client, message)
                else:
                    send_serialized(client, message)


    '''
        УВЕДОМЛЯЕТ КЛИЕНТОВ СПИСКОМ ПОДКЛЮЧЕННЫХ
    '''
    def broadcast_users_update(self, client):
        time.sleep(.1)
        message = Message()
        message.command = 'UPDATE_USERS'
        message.message = '@@@'.join(self.logins)
        self.broadcast(client, message)
        message.command = None


    '''
        ПРИНИМАЕТ ПОЛУЧАТЕЛЯ, ЕСЛИ ОН СУЩЕСТВУЕТ В АТРИБУТЕ RECIEPIENT ОБЪЕКТА СООБЩЕНИЯ
    '''
    def get_recipient(self, message):
        if message.recipient != None and message.recipient != 'None':
            index = self.logins.index(message.recipient)
            recipient = self.clients[index]
            if recipient:
                return recipient
        return None


    '''
        ВЫПОЛНЯЕТ ВЫХОД ИЗ СИСТЕМЫ КЛИЕНТА
    '''
    def logout(self, client):
        try:
            index = self.clients.index(client)
            login = self.logins[index]

            # выход
            self.server_log(client, 'Выполнен выход')

            # удаление из списка подключенных
            self.clients.remove(client)
            self.logins.remove(login)

            # уведомляет клиентов с новым списком подключенных
            self.broadcast_users_update(client)
            self._update_users_on_screen()
        finally:
            client.close()


    '''
        ВХОД КЛИЕНТА
    '''
    def make_client_login(self, client, data, message):
        if data.user in self.logins:
            # если имя уже существует, уведомляет клиента для этого использовать другое
            self.feedback_login_status(client, 'LOGIN_INVALID')
        else:
            # действительное имя
            self.logins.append(data.user)
            self.clients.append(client)
            self.feedback_login_status(client, 'LOGIN_VALID')
            self.broadcast_users_update(client)
            self._update_users_on_screen()

            # выполнить вход
            self.server_log(client, 'Выполнен вход')


    '''
        УВЕДОМИТЬ О ВХОДЕ
    '''
    def feedback_login_status(self, client, command):
        message = Message()
        message.command = command
        send_serialized(client, message)
        message.command = None


    '''
        ПРИНИМАЕТ ЛОГИН ДАННЫМ КЛИЕНТОМ
    '''
    def get_login_by_client(self, client):
        index = self.clients.index(client)
        return self.logins[index]
        

    '''
        ПОЛУЧАЕТ ФАЙЛ ОТ КЛИЕНТА И СОХРАНЯЕТ ЕГО НА СЕРВЕРЕ
    '''
    def server_receive_save_file(self, client, message, threadId):

        the_recipient = None
        received_file_name = message # получает имя загруженного файла
        saved_file_name = f'{threadId}.jpg' # генерирует уникальное имя для сохранения полученного файла

        # если он не существует, создает каталог, в котором будут сохранены файлы на сервере
        if not path.isdir('server_files'):
            try:
                os.mkdir('server_files', 777)
            except:
                pass

        # открывает файл для сохранения на сервере
        arq = open(f'server_files{os.path.sep}{saved_file_name}', 'wb')

        # начать запись нового файла
        cont = 0
        while message:
            if cont > 0:
                # в первую очередь итерация пропускает, так как именно там ему было присвоено имя файла
                # при получении флага b done завершает написание
                if cont == 1:
                    the_recipient = message.decode()
                elif message == b'done':
                    break
                else:
                    arq.write(message)
                message = client.recv(1024)
            else:
                # пропустить первое сообщение (в файле)
                message = client.recv(1024) 
            cont = cont + 1

        # закрыть файл
        arq.close()
        time.sleep(.5)

        # после сохранения файла на сервере уведомляет получателей
        # так что те же самые, где они хотят сохранить там, в их среде
        # клиент уведомит об этом после этого, чтобы сервер мог продолжить
        message = Message()
        if the_recipient != None and the_recipient != 'None':
            message.recipient = the_recipient
        message.command = 'REQUEST_PATH'
        message.message = f'{received_file_name.decode()}'
        message.user = self.get_login_by_client(client)
        self.broadcast(client, message)

        # глобально сохраняет имя загруженного файла и имя файла, сохраненного на сервере
        # эта информация будет использоваться на следующем шаге (при отправке получателям)
        self.the_file = [saved_file_name, received_file_name]

        # лог отправка файла
        self.server_log(client, f'Файл: {received_file_name.decode()}', self.get_recipient(message))

        message.command = None
        message.recipient = None
        message.message = None
        message.user = None
        

    '''
        ОТПРАВЛЯЕТ ПОЛУЧАТЕЛЯМ ТОЛЬКО ЧТО СОХРАНЕННЫЙ ФАЙЛ НА СЕРВЕРЕ
    '''
    def server_send_file_to_client(self, client):

        # отправляет имя отправленного файла (поскольку клиент сохранит его с тем же именем)
        client.send(self.the_file[1])
        time.sleep(.1)

        # открывает сохраненный файл на сервере, читает его содержимое и отправляет клиенту
        arq2 = open(f'server_files{os.path.sep}{self.the_file[0]}', 'rb')
        data = arq2.read()
        client.send(data)
        time.sleep(.1)

        # отправляет флаг done клиенту, чтобы он мог закрыть файл на своей стороне
        client.send(b'done')
        time.sleep(.1)

        # закрывает файл, который был прочитан
        arq2.close()


    '''
        ЗАПИСЬ ЛОГОВ (В ФАЙЛЕ, ЭКРАНЕ И ТЕРМИНАЛЕ)
    '''
    def server_log(self, client, complement, recipient=None):
        now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        client_ip = client.getsockname()[0]
        client_login = self.get_login_by_client(client)

        if (recipient == None):
            text_to_log = f'{now}; {client_ip}; {client_login}; {complement}'
        else:
            recipient_ip = recipient.getsockname()[0]
            recipient_login = self.get_login_by_client(recipient)
            text_to_log = f'{now}; {client_ip}; {client_login}; {recipient_ip}; {recipient_login}; {complement}'

        logging.basicConfig(filename='file.log', filemode='w', format='%(message)s')
        logging.warning(text_to_log)
        self._show_message_on_screen(text_to_log)
        print(text_to_log)


    '''
        ПРОСЛУШИВАЕТ СООБЩЕНИЯ / УВЕДОМЛЕНИЯ, ОТПРАВЛЕННЫЕ КЛИЕНТАМИ
    '''
    def handle(self, client, threadId):
        while True:
            message = Message()
            try:
                b_data = client.recv(1024)
                if b_data:
                    try:
                        data = get_serialized_message(client, b_data)

                        # запрос клиента
                        if data.command == 'LOGIN':
                            self.make_client_login(client, data, message)

                        # клиент запросил выход из системы
                        elif data.command == 'LOGOUT':
                            message = Message()
                            message.command = 'LOGOUT_DONE'
                            send_serialized(client, message)
                            message.command = None
                            time.sleep(.1)
                            self.logout(client)
                            break

                        elif data.command == 'SEND_PATH':
                            self.server_send_file_to_client(client)

                        elif data.command == 'CLEAR':
                            self.server_log(client, f'Очистил чат', self.get_recipient(data))
                            self.broadcast(client, data)

                        elif data.command == 'THEME':
                            self.server_log(client, f'Сменил тему', self.get_recipient(data))
                            self.broadcast(client, data)

                        else:
                            self.server_log(client, f'Сообщение: {data.message}', self.get_recipient(data))
                            self.broadcast(client, data)

                    except:
                        try:
                            self.server_receive_save_file(client, b_data, threadId)
                        except Exception as e:
                            pass
                else:
                    self.logout(client)
                    break
            except Exception as e:
                self.logout(client)
                break


    '''
        ПОЛУЧАЕТ НОВЫЕ СВЯЗИ ОТ КЛИЕНТОВ
    '''
    def receive(self):
        while True:
            message = Message()
            client, address = self.server.accept()

            data = get_serialized_message(client)
            self.make_client_login(client, data, message)
            
            threadId = str(uuid.uuid4())
            threading.Thread(target=self.handle, args=(client, threadId)).start()


    '''
        ОБРАТНЫЙ ВЫЗОВ, КОТОРЫЙ ПРОСЛУШИВАЕТ, КОГДА ОКНО ЗАКРЫТО
    '''
    def _close_callback(self):
        os._exit(0)
        self.window.destroy()


    '''
        МЕТОД, КОТОРЫЙ ИНИЦИАЛИЗИРУЕТ СИСТЕМУ
    '''
    def run(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('127.0.0.1', 10000))
        self.server.listen()
        print('Запуск сервера...')
        threading.Thread(target=self.receive).start()
        self.window.mainloop()


Server().run()