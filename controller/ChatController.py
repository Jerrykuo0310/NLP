from PyQt5.QtWidgets import QListWidgetItem, QMessageBox, QDialog
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize
from PyQt5 import QtWidgets, QtGui, QtCore,uic

import threading
import os
import subprocess
import win32api,win32con


from .AddContactController import AddContactController
from view import AddContactView


class MessageListener(threading.Thread):

    def __init__(self, controller, user_id):
        super(MessageListener, self).__init__()
        self.controller = controller
        self.user_id = user_id
        self.__running = True

    def terminate(self):
        self.__running = False

    def run(self):
        while self.__running:
            # time.sleep(1)
            message_queue = self.controller.model.message_queue
            self.controller.update_messages(self.user_id)
            while not message_queue.empty():
                msg = message_queue.get()
                self.controller.server.send_message(msg['sender'], msg['content'], msg['receiver'])


class ChatController:
    M = 0
    def __init__(self, view, model, server):
        self.view = view
        self.model = model
        self.server = server
        self.msg_listener = None

    @staticmethod
    def get_username(string):
        return " ".join(string.split(" ")[:-1])

    def init_view(self):
        self.init_contacts()
        self.view.sendButton.setDisabled(True)
        self.setup_view_action()
        self.msg_listener = MessageListener(self, self.model.myself['user_id'])
        self.msg_listener.start()

    def init_contacts(self):
        for contact in self.model.contacts:
            item = QListWidgetItem(QIcon('../assets/avatar/%s' % contact['avatar']),
                                   contact['username'] + " (" + str(contact['user_id']) + ")")
            self.view.contactList.addItem(item)
            self.model.messages[contact['user_id']] = []
        self.view.contactList.setIconSize(QSize(25, 25))

    def setup_view_action(self):
        view = self.view
        view.textEdit.returnPressed.connect(self.send_message)
        view.deleteButton.clicked.connect(self.delete_contact)
        view.sendButton.clicked.connect(self.send_message)
        view.contactList.itemClicked.connect(self.change_contact)
        view.newButton.clicked.connect(self.add_contact)
        view.predictButton.clicked.connect(self.predict_contact)

    def init_user(self):
        self.view.usernameLabel.setText(self.model.myself['username'])
        self.init_avatar()

    def init_avatar(self):
        pix = self.get_avatar()
        self.view.avatarLabel.setPixmap(pix)

    def get_avatar(self):
        myself = self.model.myself
        return QPixmap('../assets/avatar/%s' % myself['avatar']).scaled(40, 40)

    def delete_contact(self):  # Action when delete button pressed
        items = self.view.contactList.selectedItems()
        for item in items:
            username = self.get_username(item.text())
            user_id = self.model.get_user_id_by_name(username)
            if username != self.model.myself['username']:
                result = QMessageBox.warning(QMessageBox(), 'Are you sure?',
                                             'You will permanently delete all the records with %s.' % username,
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if result == QMessageBox.Yes:
                    self.view.contactList.takeItem(self.view.contactList.row(item))
                    self.change_contact(self.view.contactList.selectedItems()[0])
                    self.model.delete_contact(user_id)

    def change_contact(self, item):  # Action when click corresponding user
        username = self.get_username(item.text())
        user_id = self.model.get_user_id_by_name(username)
        print(user_id, self.model.contacts)
        self.view.sendButton.setDisabled(False)
        self.view.conversationList.clear()
        self.get_messages(user_id)
        self.model.change_contact(user_id)

    def predict_contact(self, user_id):

        if M == 1:
            os.system("predict.bat")
            with open('result1.tsv', 'r') as i:
                with open('E:/sentiment analysist/src/output/test_results.tsv', 'r') as j:
                    lines2 = j.readlines()  # 读取所有行
                    last_line2 = lines2[-1]  # 取最后一行
                    testline = last_line2.split("\t")
                    index = 0
                    for i in testline:
                        testline[testline.index(i)] = float(i)
                    valueStore = testline[0]
                    for i in testline:
                        if i > valueStore:
                            valueStore = i
                            index = testline.index(i)
                    if index == 0:
                        last_lineok = "----(￣ー￣) \n Emotional status:others"
                    elif index == 1:
                        last_lineok = "----(╬▔皿▔) \n Status:angry(SUGGESTED:Don't mess with him/her)"
                    elif index == 2:
                        last_lineok = "----*〒_〒* \n Status:sad(SUGGESTED:Comfort him/her)"
                    elif index == 3:
                        last_lineok = "----＼(^o^)／ \n Status:happy"
                    prediction = QListWidgetItem(last_lineok)
                    
                    #prediction.setTextColor(QColor(Qt.red))
                    self.view.conversationList.addItem(prediction)
        elif M != 1:
            win32api.MessageBox(0, "You are not VIP to predict", "Warning", win32con.MB_OK)

    def update_messages(self, user_id):
        messages = self.server.display_message(user_id)
        myself = self.model.myself
        for message in messages:
            current_user = self.model.current_user
            if myself['user_id'] == message['sender']:
                user_id = message['receiver']
            else:
                user_id = message['sender']
            try:
                if message['sender'] != message['receiver']:
                    self.model.messages[user_id].append(message)
            except:
                if user_id == myself['user_id']:
                    return
                contact = {
                    'user_id': user_id,
                    'username': self.server.get_username_by_id(user_id),
                    'avatar': 'default.jpg'
                }
                self.model.contacts.append(contact)
                item = QListWidgetItem(QIcon('../assets/avatar/%s' % contact['avatar']),
                                       contact['username'] + " (" + str(contact['user_id']) + ")")
                self.view.contactList.addItem(item)
                self.model.messages[user_id] = [message]

            if current_user and user_id == current_user['user_id']:
                global M
                M = user_id
                '''
                with open('E:/sentiment analysist/src/bert/test2.tsv', 'a') as g:  # txt zai zhe l
                    with open('E:/sentiment analysist/src/bert/test1.tsv', 'a') as h:  # txt zai zhe li
                        with open('result1.tsv', 'r') as i:
                            with open('E:/sentiment analysist/src/output/test_results.tsv', 'r') as j:
                                lines1 = i.readlines()  # 读取所有行
                                last_line1 = lines1[-1]  # 取最后一行
                                lines2 = j.readlines()  # 读取所有行
                                last_line2 = lines2[-1]  # 取最后一行
                                testline = last_line2.split("\t")
                                index = 0
                                for i in testline:
                                    testline[testline.index(i)] = float(i)
                                valueStore = testline[0]
                                for i in testline:
                                    if i > valueStore:
                                        valueStore = i
                                        index = testline.index(i)
                                if index == 0:
                                    last_lineok = "--others"
                                elif index == 1:
                                    last_lineok = "--angry"
                                elif index == 2:
                                    last_lineok = "--sad"
                                elif index == 3:
                                    last_lineok = "--happy"
                                item1 = QListWidgetItem(QIcon('../assets/avatar/%s' % current_user['avatar']),message['content'] + '\n')
                                item2 = QListWidgetItem(QIcon('../assets/avatar/%s' % current_user['avatar']),message['content'] + '\n' + last_lineok)'''
                with open('E:/sentiment analysist/src/bert/test2.tsv', 'a') as g:  # txt zai zhe l
                    with open('E:/sentiment analysist/src/bert/test1.tsv', 'a') as h:  # txt zai zhe li
                        item = QListWidgetItem(QIcon('../assets/avatar/%s' % current_user['avatar']), message['content'] )#情感分析放这里
                        if user_id % 2 == 0:
                            h.write(message['content'] + '\n')
                            self.view.conversationList.addItem(item)
                            M = user_id
                        elif user_id % 2 == 1:
                            g.write(message['content'] + '\n')
                            self.view.conversationList.addItem(item)
                            M = user_id
                                #self.view.conversationList.addItem(item)

    def get_messages(self, user_id):  # zaizheligao Get messages of current user
        # Init user information
        user = self.model.get_user_by_id(user_id)
        myself = self.model.myself

        message_list = self.model.messages[int(user_id)]
        with open('test.tsv', 'w') as f:  # txt zai zhe li
            for message in message_list:
                if message['sender'] == myself['user_id']:
                    f.write(message['content'] + '\n')
                    item = QListWidgetItem(QIcon('../assets/avatar/%s' % myself['avatar']), message['content'])

                else:
                    f.write(message['content'] + '\n')
                    item = QListWidgetItem(QIcon('../assets/avatar/%s' % user['avatar']), message['content'])
                self.view.conversationList.addItem(item)

            self.view.conversationList.setIconSize(QSize(25, 25))

    def send_message(self):
        content = self.view.textEdit.toPlainText()
        if not content:
            QMessageBox.warning(QMessageBox(), 'Warning', 'You could not send an empty string.', QMessageBox.Ok, QMessageBox.Ok)
            return
        myself = self.model.myself
        self.model.send_message(content)
        item = QListWidgetItem(QIcon('../assets/avatar/%s' % myself['avatar']), content)
        self.view.conversationList.addItem(item)
        # item.view.setGeometry(QtCore.QRect(460, 10, 611, 441))
        self.view.conversationList.setIconSize(QSize(25, 25))
        self.view.textEdit.clear()

    def add_contact(self):  # Pop out add contact window
        dialog = QDialog()
        view = AddContactView(dialog)
        controller_add = AddContactController(self, view, self.model)
        dialog.exec()

    def stop_and_exit(self):
        self.msg_listener.terminate()
        self.msg_listener.join()
        self.server.user_leave(self.model.myself['user_id'])

