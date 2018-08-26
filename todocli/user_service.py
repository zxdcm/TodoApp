from todocli.user import User
import configparser


class UserService:

    def __init__(self, session, config_file):
        self.config_file = config_file
        self.config_parser = configparser.ConfigParser()
        self.session = session

    def login_user(self, username):
        user = self.get_user(username)
        if user:
            self.config_parser['user'] = {}
            self.config_parser['user']['username'] = user.username
            with open(self.config_file, 'w') as configfile:
                self.config_parser.write(configfile)
        return user

    def logout_user(self):
        self.config_parser['user'] = {}
        with open(self.config_file, 'w') as configfile:
            self.config_parser.write(configfile)

    def get_current_user(self):
        username = None
        try:
            self.config_parser.read(self.config_file)
            username = self.config_parser['user']['username']
        except BaseException:
            pass
        return self.login_user(username)

    def get_all_users(self):
        return self.session.query(User).all()

    def get_user(self, username):
        return self.session.query(User).filter_by(username=username).one_or_none()

    def create_user(self, username):
        if self.get_user(username) is None:
            user = User(username)
            self.session.add(user)
            self.session.commit()
            return user
        return None
