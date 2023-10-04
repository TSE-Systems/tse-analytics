from windows_toasts import Toast, WindowsToaster

toaster = WindowsToaster("TSE Analytics")


def show_notification(title: str, content: str):
    toast = Toast([title, content])
    # toast.on_activated = lambda _: print("Toast clicked!")
    toaster.show_toast(toast)
