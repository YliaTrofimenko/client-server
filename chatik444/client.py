import socket, threading, time, os
from gui_helper import *
from model import *
from utils import *

class Client:

    '''
        Иницилизация графического интерфейса приложения
    '''
    def __init__(self):
        # создание и настройка окна
        self.gui_helper = GUIHelper()
        self.window = self.gui_helper.window_build(self._close_callback)

        # метод построения элементов экрана
        self._build()

        # инициализация некоторых методов
        self.message = Message()
        self.file_path = ''

    '''
        Вызываем методы построения графического интерфейса
    '''
    def _build(self):
        self._build_message_area()
        self._build_connecteds_area()
        self._build_entry_area()
        self._build_you_area()
        self._build_actions_area()
        

    '''
        Создаем область сообщений
    '''
    def _build_message_area(self):
        self.f_messages = self.gui_helper.message_area_build(self.window, 'Входящие сообщения:')


    '''
        Создаем область подключенных пользователей
    '''
    def _build_connecteds_area(self):
        self.f_connecteds = self.gui_helper.connecteds_area_build(self.window, 'Участники:')


    '''
        Создаем область отправки сообщений
    '''
    def _build_entry_area(self):
        self.f_text = self.gui_helper.entry_area_build(self.window, 'Введите сообщение:')

    
    '''
        Создаем область отображения имени текущего пользователя
    '''
    def _build_you_area(self):
        self.f_you_label = self.gui_helper.connected_area_build(self.window, 'Ваше имя:')


    '''
        Создаем область действия кнопки
    '''
    def _build_actions_area(self):
        actions = self.gui_helper.actions_area_build(self.window, self._send_message, self._send_file, self._clear,
                                                     self._theme, self._desconnect, self._popup)
        self.f_send, self.f_file, self.f_clear, self.f_theme, self.f_logout, self.f_connect = actions


    '''
        Создаем метод всплывающего окна для входа в систему
    '''
    def _popup(self):
        self.popup = self.gui_helper.login_popup_build(self.window, 'Войти', self._open_popup_callback,
                                                       self._close_popup_callback)
        self.popup.mainloop()


    '''
        Метод построения элементов экрана всплывающего окна
    '''
    def _open_popup_callback(self, popup):
        self.f_login, self.f_do_login, self.f_label_fail = self.gui_helper.login_popup_elements_build(popup, 'Введите свое имя', self._do_login)
        self.f_connect['state'] = DISABLED
        self.f_connect['background'] = '#8d99ae'

    
    '''
        Включает кнопки когда пользователь вошел в систему
    '''
    def _enable_actions(self):
        self.gui_helper.enable_actions(self)

    
    '''
        Отключает кнопки когда пользователь отключен
    '''
    def _disable_actions(self):
        self.gui_helper.disabled_actions(self)


    '''
        Метод который проверяет форму входа и выполняет вход
    '''
    def _do_login(self):
        if (not self.f_login.get()):
            self._show_validation_error('Обязательное поле.')
        else:
            self.message.user = self.f_login.get()
            self.message.command = 'ВОЙТИ'

            # вызов метода для подключения клиента
            if not self._connect_client():
                self._show_validation_error('Сервер недоступен.')
            else:
                self.f_you_label['text'] = self.message.user


    '''
        МЕТОД, КОТОРЫЙ СОЕДИНЯЕТ КЛИЕНТА С СЕРВЕРОМ (ВЫЗЫВАЕТСЯ ЛОГИНОМ)
    '''
    def _connect_client(self):
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.client.connect_ex(('127.0.0.1', 10000)) == 0:
                send_serialized(self.client, self.message)
                threading.Thread(target=self._receive).start()
            else:
                send_serialized(self.client, self.message)
            return True
        except Exception as e:
            return False


    '''
        СИСТЕМА ПОКАЗЫВАЕТ СООБЩЕНИЕ ОБ ОШИБКЕ НА ЭКРАНЕ ВХОДА В СИСТЕМУ
    '''
    def _show_validation_error(self, message):
        self.f_label_fail['text'] = message
        self.f_label_fail.grid(row=2, column=0)


    '''
        СИСТЕМА ОТОБРАЖАЕТ ВХОДЯЩИЕ СООБЩЕНИЯ НА ЭКРАНЕ
    '''
    def _show_message_on_screen(self, message):
        self.gui_helper.update_message_area(self.f_messages, message)


    '''
        СИСТЕМА ОБНОВЛЯЕТ ВОШЕДШИХ В СИСТЕМУ ПОЛЬЗОВАТЕЛЕЙ НА ЭКРАНЕ
    '''
    def _update_users_on_screen(self, message):
        users = message.split('@@@')
        self.users = []
        self.f_connecteds.delete(0,END)
        self.f_connecteds.insert(0, 'Вы')
        i = 1
        for user in users:
            if user != self.message.user:
                self.f_connecteds.insert(i, user)
                self.users.append(user)
                i = i + 1
        self.f_connecteds.select_set(0)



    def _set_the_recipient(self):
        selected = self.f_connecteds.curselection()
        if selected and selected[0] != 0:
            self.message.recipient = self.users[selected[0] - 1]
        else:
            self.message.recipient = None

    '''
        СИСТЕМА ЧИСТИТ СООБЩЕНИЯ НА ЭКРАНЕ
    '''

    def _clear(self):
        self.message.message = 'очистил чат'
        self.message.command = 'CLEAR'
        send_serialized(self.client, self.message)
        self.message.message = ''
        self.message.command = None

    def _theme(self):
        global switch_value
        switch_value = False
        self.message.message = 'сменил тему'
        self.message.command = 'THEME'
        send_serialized(self.client, self.message)
        self.message.message = ''
        self.message.command = None
        if switch_value:  # dark
            self.window.configure(bg='#2b2b2b')
            self.f_messages.configure(bg='#2b2b2b', fg='#89b0c4')
            self.f_connecteds.configure(bg='#2b2b2b', fg='#89b0c4')
            self.f_text.configure(bg='#2b2b2b', fg='#89b0c4')
            self.f_you_label.configure(bg='#2b2b2b', fg='#89b0c4')
            self.f_label_fail.configure(bg='#2b2b2b')
            self.f_login.configure(bg='#2b2b2b', fg='#89b0c4')
            switch_value = False
        else:  # light
            self.window.configure(bg='#FCFCEE')
            self.f_messages.configure(bg='#FCFCEE', fg='#0A0A0A')
            self.f_connecteds.configure(bg='#FCFCEE', fg='#0A0A0A')
            self.f_text.configure(bg='#FCFCEE', fg='#0A0A0A')
            self.f_you_label.configure(bg='#FCFCEE', fg='#0A0A0A')
            self.f_label_fail.configure(bg='#FCFCEE')
            self.f_login.configure(bg='#FCFCEE', fg='#0A0A0A')
            switch_value = True
        return

    '''
        МЕТОД, КОТОРЫЙ ОТПРАВЛЯЕТ СООБЩЕНИЕ ОТ КЛИЕНТА К СЕРВЕРУ
    '''
    def _send_message(self):
        text = self.f_text.get()
        if text:
            self._set_the_recipient()
            self.message.message = text
            self.message.command = 'MESSAGE'
            send_serialized(self.client, self.message)
            self.message.command = None
            self.f_text.delete(0, END)
            self.f_text.insert(0, '')


    '''
        МЕТОД, КОТОРЫЙ ОТПРАВЛЯЕТ ВЫБРАННЫЙ КЛИЕНТОМ ФАЙЛ НА СЕРВЕР
    '''
    def _send_file(self):
        self._set_the_recipient()

        # запрашивает файл
        file_path = filedialog.askopenfilename(initialdir = os.path.sep, title = 'Выберите файл')

        if (file_path and file_path != None and file_path != ''):
            file_info  = file_path.split('/')
            file_name = file_info.pop()
            recipient = 'None'
            
            # получатель получает если он существует
            if self.message.recipient != None:
                recipient = self.message.recipient

            # отправляет имя выбранного файла
            self.client.send(file_name.encode())
            time.sleep(.1)

            # отправляет имя получателя (если оно существует)
            self.client.send(recipient.encode())
            time.sleep(.1)

            # отправляет выбранный файл
            selected_file = open(file_path,'rb')
            data = selected_file.read()
            self.client.send(data)
            time.sleep(.1)

            # отправляет флаг, сигнализирующий, что файл был загружен
            self.client.send('done'.encode())
            time.sleep(.1)

            # закрыть файл
            selected_file.close()


    '''
        МЕТОД, КОТОРЫЙ ОБНОВЛЯЕТ КАТАЛОГ, В КОТОРОМ ПОЛЬЗОВАТЕЛЬ СОХРАНИТ ПОЛУЧЕННЫЙ ФАЙЛ
ВЫЗЫВАЕТСЯ ВСЯКИЙ РАЗ, КОГДА КТО-ТО ОТПРАВЛЯЕТ ВАМ ФАЙЛ
    '''
    def _send_file_path(self):
        # выбирает каталог
        self.file_path = None
        self.file_path = filedialog.askdirectory()
        if (self.file_path and self.file_path != None and self.file_path != ''):

            # уведомляет сервер о том, что каталог сохранения был обновлен
            time.sleep(.1)
            self.message.command = 'SEND_PATH'
            send_serialized(self.client, self.message)
            self.message.command = None


    '''
        МЕТОД ПОСЛЕ ТОГО, КАК СЕРВЕР СОХРАНИЯЕТ ЗАГРУЖЕННЫЙ ФАЙЛ СРАЗУ ОТПРАВЛЯЕТ ЕГО ПОЛУЧАТЕЛЯМ
    '''
    def client_receive_save_file(self, data):

        # извлекает имя загруженного файла (который сервер передал)
        send_filename = data

        # создает файл с выбранным каталогом и тем же именем, что и загруженный файл
        save_as = f'{self.file_path}{os.path.sep}{send_filename.decode()}'
        arq = open(save_as, 'wb')

        cont = 0
        while data:

            if cont > 0:
                if data == b'done':
                    arq.close()
                    break
                
                # записывает полученный контент в файл
                arq.write(data)
                data = self.client.recv(1024)
            else:
                # пропускает первое сообщение (где было получено имя файла)
                data = self.client.recv(1024)
                cont = cont + 1

        # закрывает сохраненный файл
        arq.close()


    '''
        МЕТОД, КОТОРЫЙ ПРОСЛУШИВАЕТ СООБЩЕНИЯ, ОТПРАВЛЕННЫЕ СЕРВЕРОМ
        (В ПОТОКЕ)
    '''
    def _receive(self):
        while True:
            try:
                b_data = self.client.recv(1024)
                if b_data:

                    try:
                        # сообщения в целом
                        data = get_serialized_message(self.client, b_data)

                        # ошибка входа в систему
                        if data.command == 'LOGIN_INVALID':
                            self._disable_actions()
                            self._show_validation_error('Пожалуйста, выберите другое имя.')
                        
                        # успешный вход
                        elif data.command == 'LOGIN_VALID':
                            self.message.command = None
                            self._enable_actions()
                            self.popup.destroy()

                        # обновить список подключенных
                        elif data.command == 'UPDATE_USERS':
                            self.message.command = None
                            self._update_users_on_screen(data.message)

                        # получить сообщение
                        elif data.command == 'MESSAGE':
                            self._show_message_on_screen(f'{data.user}: {data.message}')

                        # очистить консоль
                        elif data.command == 'CLEAR':
                            self.f_messages.configure(state='normal')
                            self.f_messages.delete('1.0', END)
                            self._show_message_on_screen(f'Пользователь {data.user} {data.message}')

                        # сменить тему
                        elif data.command == 'THEME':
                            self._show_message_on_screen(f'Пользователь {data.user} {data.message}')

                        # выберите, где сохранить файл
                        elif data.command == 'REQUEST_PATH':
                            self._show_message_on_screen(f'{data.user}: {data.message}')
                            self._send_file_path()

                        # отключить клиент
                        elif data.command == 'LOGOUT_DONE':
                            self._reset_gui()
                            self.client.close()
                            break

                    except:
                        self.client_receive_save_file(b_data)
                        
                else:
                    self.client.close()
                    break
            except Exception as e:
                self.client.close()
                break

    
    '''
        ОБРАТНЫЙ ВЫЗОВ, КОТОРЫЙ ПРОСЛУШИВАЕТ, КОГДА ОКНО ЗАКРЫТО
    '''
    def _close_callback(self):
        self.window.destroy()
        self.client.close()
        try:
            self.popup.destroy()
        except Exception as e:
            pass


    '''
        МЕТОД, КОТОРЫЙ ЗАПРАШИВАЕТ СЕРВЕР ОТКЛЮЧАЕТ КЛИЕНТ
    '''
    def _desconnect(self):
        self.message.command = 'LOGOUT'
        send_serialized(self.client, self.message)
        self.message.command = None

    
    '''
        ОБРАТНЫЙ ВЫЗОВ, КОТОРЫЙ ПРОСЛУШИВАЕТ, КОГДА ВСПЛЫВАЮЩЕЕ ОКНО ЗАКРЫТО
    '''
    def _close_popup_callback(self):
        self.popup.destroy()

        self.f_connect['state'] = NORMAL
        self.f_connect['background'] = '#64a6bd'


    '''
        МЕТОД, КОТОРЫЙ СБРАСЫВАЕТ ЭКРАН ПОСЛЕ ВЫХОДА ПОЛЬЗОВАТЕЛЯ ИЗ СИСТЕМЫ
    '''
    def _reset_gui(self):
        self._disable_actions()
        self.f_you_label['text'] = ''
        self.f_connecteds.delete(0, END)
        self.f_messages.configure(state='normal')
        self.f_messages.delete('1.0', END)
        self.f_messages.configure(state='disabled')

    
    '''
       МЕТОД, КОТОРЫЙ ИНИЦИАЛИЗИРУЕТ ИНТЕРФЕЙС
    '''
    def run(self):
        self.window.mainloop()
    

Client().run()