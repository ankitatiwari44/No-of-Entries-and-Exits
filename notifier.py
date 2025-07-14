from plyer import notification

def send_notification(message):
    notification.notify(
        title="People Counter Alert",
        message=message,
        timeout=5
    )
