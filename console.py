from general_functionality import update_winrates_in_db, update_full_db, download_images


def console_handler():
    command_dict = {
        'update': update_winrates_in_db,
        'full_update': update_full_db,
        'download_images': download_images
    }
    help_ = """Command list:
    update - updating winrates in database
    full_update - update db from scratch (all tables)
    download_images - download hero images
    push - upload database to github
    push_images - upload images to github
    exit - close app"""

    print(help_)

    while True:
        user_command = input("Choose command: ")
        if user_command == 'exit':
            break

        if user_command not in command_dict:
            raise NotImplementedError('This command is not implemented yet')

        command_dict[user_command]()
