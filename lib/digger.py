from lib.user import User
from lib.google_people_api import GooglePeopleApi
from time import sleep


class Digger:
    def __init__(self, mails, browser):
        self.users = None
        self._create_users(mails=mails, browser=browser)

    def _create_users(self, mails, browser):
        self.gpa = GooglePeopleApi(mails=mails)
        if not self.gpa.connected:
            self.users = [User(mail=mail, browser=browser) for mail in mails]
            return

        users_info = []
        while True:
            data = self.gpa.get_data()
            users_info.extend(data)

            if len(self.gpa.mails) == 0:
                break
            sleep(2)

        self.users = [User(browser=browser, **user_info) for user_info in users_info]

    def as_dict(self):
        return [user.as_dict() for user in self.users]
