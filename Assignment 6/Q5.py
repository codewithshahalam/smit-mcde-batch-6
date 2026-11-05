# Q5. Notification Dispatcher - Polymorphism

class EmailNotification:
    def send(self, message):
        print(f"Email notification: {message}")


class SMSNotification:
    def send(self, message):
        print(f"SMS notification: {message}")


class PushNotification:
    def send(self, message):
        print(f"Push notification: {message}")


class WhatsAppNotification:
    def send(self, message):
        print(f"WhatsApp notification: {message}")


def notify_all(notifications, message):
    for notification in notifications:
        notification.send(message)


if __name__ == "__main__":
    notification_services = [
        EmailNotification(),
        SMSNotification(),
        PushNotification(),
        WhatsAppNotification()
    ]
    notify_all(notification_services, "Your order has been shipped.")

    print("\nPolymorphism occurs when notify_all() calls the same send() method on different object types. The dispatcher does not need to know each object's class.")