
from services import AppService

if __name__ == '__main__':
    #user = AppService.create_user(name='username', email='user')
    api = AppService('user')
    api.create_task('name', 'descr')
    print(api.get_user_folders())
    [print(x.description) for x in api.get_user_tasks()]
