
from services import AppService

if __name__ == '__main__':
    user = AppService.create_user(name='username', email='user')
    try:
        user.save()
    except:
        user = AppService.get_user('user')
    api = AppService(user)
    api.create_folder('Test Folder')
    for item in api.get__user_folders():
        print(item.name)
    print(api.get_folder_by_id(1).name)
