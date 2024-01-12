from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import OrderItem

 
@receiver(post_save, sender=OrderItem) 
def create_profile(sender, instance, created, **kwargs):
    if created:               
        print("signal calls") 
                             





                           