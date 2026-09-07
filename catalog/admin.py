from django.contrib import admin
from catalog.models import User, Genre, Director, Movie, UserMovie

from django.contrib.auth.admin import UserAdmin

# Register your models here.


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "year_of_birth")
    search_fields = ("first_name", "last_name")


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'director', 'release_year')
    search_fields = (
        "title",
        "director__first_name",
        "director__last_name",
    )
    list_filter = ('director', 'release_year')


@admin.register(UserMovie)
class UserMovieAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'watched',)
    search_fields = ('user__username', 'movie__title')
    list_filter = ('watched',)
