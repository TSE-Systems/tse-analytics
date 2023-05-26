from win11toast import notify


def show_notification(title: str, content: str):
    notify(title, content, app_id="TSE Analytics")
