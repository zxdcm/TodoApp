from client import __main__

if __name__ == '__main__':
    __main__.main()
    # AppService().create_user('user')
    # service = AppService()
    # task = service.create_task(2, name='test', start_date=datetime.now())
    # task = service.add_subtask(user_id=2, task_id=task.id, )
    # #service.share_task_on_write(user_receiver_id=1, user_creator_id=2, task_id=task.id)
    # sys.exit()
    # main_parser = parse_args()
    # service = AppService()
    #service.create_task(1, name='test', start_date=datetime.now())

    # dict = {'start_date': datetime.now()}
    # for x in service.get_own_tasks(1):
    #     service.update_task(user_id=1, task_id=x.id, args=dict)
    # repeat = service.create_repeat(
    #     user_id=1, task_id=1, repetitions_amount=2, end_date=datetime.now() + timedelta(5), period_amount=2, period_type='Min')
    # print(repeat)
    #
    # sub_list = service.get_subtasks(user_id=1, task_id=1)
    # for x in sub_list:
    #     print(x)
    # service.create_task(user_id=1, name='test')
    # task = service.get_frozen_task_by_id(user_id=1, task_id=1)
    # try:
    #     task.name = 'Test'
    # except TypeError:
    #     print('bingo')
    # task = service.create_task(user_id=1, name='test', priority='Low')
    # [print(x) for x in service.get_own_tasks(1)]
    # service.share_task_on_write(user_owner_id=1, task_id=1, user_receiver_id=2)
    # task = service.get_task_by_id(user_id=1, task_id=1)
    # print(task.repeat)
    #
    # sys.exit()
    # # print(repeat)
    # # repeat = service.get_repeat_by_id(user_id=user_id, repeat_id=1)
    # # r_list = service.get_all_repeats(user_id=1)
    # print(service.user_can_write_task(2, 1))
    # #task = service.create_task(user_id=2, name='test2')
    # #service.create_repeat(2, task.id, period_amount=1, period_type='day')
    # # for x in service.get_shared_repeats(user_id=2):
    # #     print(x)
    # for x in service.get_created_repeats(user_id=2):
    #     print(x)
    # print(service.share_task_on_write(user_owner_id=1, task_id=1, user_receiver_id=2))
    # print(service.user_can_write_task(user_id=2, task_id=1))

    # service.share_task_on_write(user_owner_id=1, user_receiver_id=2, task_id=1)
    # repeat = service.create_repeat(user_id=1, task_id=2, period_amount=1)

    # service.save()
    #    service.get_observable_tasks(1)
    #    service.user_can_read_task(user_id=1, task_id=5)
    # args = main_parser.parse_args()
    # args.user_id = 1
    # commands_handler(service, args)
    # print(args)
