from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import OrderItem
from notifypy import Notify


# Notification function
def notification():
    # Create a notification object
    notification = Notify()

    # Set the title and message for the notification
    notification.title = "New order received."

    # Set the path to the notification icon
    notification.icon = "/home/cis/Downloads/notification.png"

    # Display the notification 
    notification.send() 


@receiver(post_save, sender=OrderItem) 
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Call function
        notification() 