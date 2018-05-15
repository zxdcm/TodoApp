

from models import test_func_create_folder, create_tables, test_func_get_folders


if __name__ == '__main__':
    try:
        create_tables()
    except:
        pass
    for folder in test_func_get_folders():
        print(f'{folder.name}')
