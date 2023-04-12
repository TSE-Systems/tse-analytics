from win11toast import toast


def show_notification(title: str, content: str):
    toast(title, content, app_id="TSE Analytics")
