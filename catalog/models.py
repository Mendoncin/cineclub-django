from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    pass


class Genre(models.Model):
    name = models.CharField(max_length=200, help_text="Enter a movie genre (e.g. Action, Comedy, Drama)")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
