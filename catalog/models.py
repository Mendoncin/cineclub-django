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


class Director(models.Model):
    first_name = models.CharField(max_length=100, help_text="Enter the director's first name")
    last_name = models.CharField(max_length=100, help_text="Enter the director's last name")
    year_of_birth = models.PositiveIntegerField(null=True, blank=True, help_text="Enter the director's year of birth")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['last_name', 'first_name']


class Movie(models.Model):
    title = models.CharField(max_length=200, help_text="Enter the movie title")
    description = models.TextField(help_text="Enter a brief description of the movie")
    release_date = models.DateField(help_text="Enter the release date of the movie")
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this movie")
    director = models.ForeignKey(Director, on_delete=models.SET_NULL, null=True, help_text="Select the director for this movie")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class UserMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="Select the user")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, help_text="Select the movie")
    watched = models.BooleanField(default=False, help_text="Has the user watched this movie?")

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "movie"],
                name="unique_user_movie"
            )
        ]
        ordering = ["user", "movie"]
