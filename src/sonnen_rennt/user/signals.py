from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

from rest_framework.authtoken.models import Token


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        token = Token.objects.create(user=instance)
        print("Token:", token.key)

        Profile(user=instance, name=instance.username).save()
        # Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    print("save_profile Profile 1")
    instance.profile.save()
