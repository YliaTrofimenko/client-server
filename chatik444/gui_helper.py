import tkinter as tk
from tkinter import *
from tkinter import filedialog

class GUIHelper():

    def __init__(self):
        pass

    '''
        ГЛАВНОЕ ОКНО
    '''
    def window_build(self, close_callback):
        window = Tk()
        window.title('Chat App by Ivan Protsko')
        window.geometry('870x700+0+0')
        window.configure(background='#2b2b2b', pady=30)
        window.protocol('WM_DELETE_WINDOW', close_callback)
        return window


    '''
        ОБЛАСТЬ СООБЩЕНИЙ
    '''
    def message_area_build(self, window, title, height=22):
        lb_messages = LabelFrame(window, text=title, height=30, background='#313335', font=('Arial', 12, 'bold'),
                                 fg='white')
        text_area = Text(lb_messages, height=height, width=59, background='#2b2b2b', font=('Arial', 14), fg='#89b0c4')
        text_area.configure(state='disabled')
        text_area.pack()
        lb_messages.grid(row=0, column=0, sticky='we', padx=10)
        return text_area


    '''
        ОБЛАСТЬ УЧАСТНИКОВ
    '''
    def connecteds_area_build(self, window, title, height=21):
        lb_connecteds = LabelFrame(window, text=title, height=30, background='#313335', font=('Arial', 12, 'bold'),
                                   fg='white')
        f_connecteds = Listbox(lb_connecteds, height=height, width=15, background='#2b2b2b', font=('Arial', 14),
                               fg='#89b0c4')
        f_connecteds.pack()
        lb_connecteds.grid(row=0, column=1)
        return f_connecteds


    '''
        ОБЛАСТЬ ВВОДА
    '''
    def entry_area_build(self, window, title):
        lb_text = LabelFrame(window, text=title, height=5, background='#313335', font=('Arial', 12, 'bold'), fg='white')
        f_text = Entry(lb_text, width=60, background='#2b2b2b', font=('Arial', 14), fg='#89b0c4')
        f_text.pack(side=LEFT)
        lb_text.grid(row=1, column=0, sticky='we', padx=10, ipady=6, pady=10)
        return f_text


    '''
        ОБЛАСТЬ УЧАСТНИКОВ
    '''
    def connected_area_build(self, window, title):
        lb_you = LabelFrame(window, text=title, height=5, background='#313335', font=('Arial', 12, 'bold'), fg='white')
        f_you_label = Label(lb_you, text='', fg='#89b0c4', background='#2b2b2b', font=('Arial', 13, 'bold'), padx=10)
        f_you_label.pack(side=LEFT)
        lb_you.grid(row=1, column=1, sticky='we', padx=10, ipady=6, pady=10)
        return f_you_label


    '''
        ОБЛАСТЬ КНОПОК
    '''
    def actions_area_build(self, window, send_action, file_action, clear_action, theme_action, logout_action,
                           login_action):
        lb_actions = LabelFrame(window, text='', height=10, background='#313335', font=('Arial', 12, 'bold'),
                                fg='white')

        f_send = Button(lb_actions, text='Отправить', width=10, command=send_action, background='#313335',
                        font=('Arial', 12), fg='white', cursor='hand2', state=DISABLED)
        f_send.pack(side=LEFT)

        f_file = Button(lb_actions, text='Прикрепить', width=10, command=file_action, background='#313335',
                        font=('Arial', 12), fg='white', cursor='hand2', state=DISABLED)
        f_file.pack(side=LEFT)

        f_clear = Button(lb_actions, text='Чистка', width=10, command=clear_action, background='#313335',
                         font=('Arial', 12), fg='white', cursor='hand2', state=DISABLED)
        f_clear.pack(side=LEFT)

        f_theme = Button(lb_actions, text='Тема', width=10, command=theme_action, background='#313335',
                         font=('Arial', 12), fg='white', cursor='hand2', state=DISABLED)
        f_theme.pack(side=LEFT)

        f_logout = Button(lb_actions, text='Выйти', width=10, command=logout_action, background='#313335',
                          font=('Arial', 12), fg='white', cursor='hand2', state=DISABLED)
        f_logout.pack(side=RIGHT)

        f_connect = Button(lb_actions, text='Войти', width=10, command=login_action, background='#499c54',
                           font=('Arial', 12), fg='white', cursor='hand2')
        f_connect.pack(side=RIGHT)

        lb_actions.grid(row=2, column=0, columnspan=2, sticky='we', ipady=5, padx=10, ipadx=10)

        return [f_send, f_file, f_clear, f_theme, f_logout, f_connect]


    '''
        ВСПЛЫВАЮЩЕЕ ОКНО
    '''
    def login_popup_build(self, window, title, open_callback, close_callback):
        popup = Tk()
        popup.configure(background='#2b2b2b', pady=30)
        popup.title(title) 
        popup.protocol('WM_DELETE_WINDOW', close_callback)

        # вызывает метод, который строит элементы всплывающего окна
        open_callback(popup)

        return popup


    '''
        СОЗДАЕМ ЭЛЕМЕНТЫ ЭТОГО ОКНА
    '''
    def login_popup_elements_build(self, popup, title, do_login_action):
        f_label_login = Label(popup, text=title, fg='white', background='#313335', font=('Arial', 12))
        f_label_login.grid(row=0, column=0)
        f_login = Entry(popup, width=30, background='#2b2b2b', font=('Arial', 14), fg='#89b0c4')
        f_login.grid(row=1, column=0, sticky='we', padx=10, ipady=6, pady=10)
        f_do_login = Button(popup, text='Войти', width=10, command=do_login_action, background='#499c54',
                            font=('Arial', 12), fg='white', cursor='hand2')
        f_do_login.grid(row=1, column=1, sticky='we', padx=10, ipady=6, pady=10)
        f_label_fail = Label(popup, text='', fg='#ef233c', background='#2b2b2b', font=('Arial', 12))

        return [f_login, f_do_login, f_label_fail]


    '''
        Конфигурация
    '''
    def enable_actions(self, context):
        context.f_send['state'] = NORMAL
        context.f_send['background'] = '#499c54'
        context.f_file['state'] = NORMAL
        context.f_file['background'] = '#89b0c4'
        context.f_clear['state'] = NORMAL
        context.f_clear['background'] = '#89b0c4'
        context.f_theme['state'] = NORMAL
        context.f_theme['background'] = '#89b0c4'
        context.f_connect['state'] = DISABLED
        context.f_connect['background'] = '#313335'
        context.f_logout['state'] = NORMAL
        context.f_logout['background'] = '#ef233c'


    def disabled_actions(self, context):
        context.f_send['state'] = DISABLED
        context.f_send['background'] = '#313335'
        context.f_file['state'] = DISABLED
        context.f_file['background'] = '#313335'
        context.f_clear['state'] = DISABLED
        context.f_clear['background'] = '#313335'
        context.f_theme['state'] = DISABLED
        context.f_theme['background'] = '#313335'
        context.f_connect['state'] = NORMAL
        context.f_connect['background'] = '#0abab5'
        context.f_logout['state'] = DISABLED
        context.f_logout['background'] = '#313335'


    def update_message_area(self, message_area, message):
        message_area.configure(state='normal')
        message_area.insert(INSERT, f'{message} \n')
        message_area.see(END)
        message_area.configure(state='disabled')
