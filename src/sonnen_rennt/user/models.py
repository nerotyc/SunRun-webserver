from django.contrib.auth.models import User
from django.db import models
from PIL import Image

# import group.models
# import run.models

# null or default for optional fields (blank=True --> can be left out)
# null -> database
# blank -> rendered field

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    joined = models.DateField('joined', auto_now=True)
    name = models.CharField('name', max_length=200, default='')
    confirmed = models.BooleanField('confirmed', default=False)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    # stared_groups = models.ManyToManyField(group.models.Group, null=True, blank=True)
    # stared_runs = models.ManyToManyField(group.models.Run, null=True, blank=True)

    ROLE_USER = "Nutzer"
    ROLE_TRAINER = "Trainer"
    ROLE_HEAD_TRAINER = "Vorstand"
    ROLE_ADMIN = "Administator"

    USER_ROLE_CHOICES = (
        (ROLE_USER, 'Nutzer'),
        (ROLE_TRAINER, 'Trainer'),
        (ROLE_HEAD_TRAINER, 'Vorstand'),
        (ROLE_ADMIN, 'Administator'),
    )

    role = models.CharField('role', max_length=200, default=ROLE_USER,
                             choices=USER_ROLE_CHOICES)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self):
        super().save()

        if self.image and self.image.path:
            img = Image.open(self.image.path)

            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)
