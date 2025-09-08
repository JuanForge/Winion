Prototype = True


from typing import Literal
from notifypy import Notify

def sendnotification(message: str, title: str = "Winion", level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'DEBUG'):
    notification = Notify(default_notification_icon="./Assets/icon.ico",
                            default_notification_title=title,
                            default_notification_audio="./Assets/3.wav",
                            default_notification_application_name="Winion"
                        )
    #notification.title = " Title"
    notification.message = message
    notification.send()