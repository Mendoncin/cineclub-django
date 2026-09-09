from django.urls import path
from catalog.views import (
    add_to_watchlist,
    index,
    MoviesListView,
    MovieDetailView,
    DirectorListView,
    DirectorDetailView,
    GenreListView,
    mark_as_watched,
    remove_from_watched,
    remove_from_watchlist,
    profile_view,
    watchlist_view,
)

app_name = "catalog"

urlpatterns = [
    path("", index, name="index"),
    path("movies/", MoviesListView.as_view(), name="movie-list"),
    path("movies/<int:pk>/", MovieDetailView.as_view(), name="movie-detail"),
    path("directors/", DirectorListView.as_view(), name="director-list"),
    path("directors/<int:pk>/", DirectorDetailView.as_view(), name="director-detail"),
    path("genres/", GenreListView.as_view(), name="genre-list"),
    path(
        "movies/<int:pk>/add_to_watchlist/",
        add_to_watchlist,
        name="add-to-watchlist"
    ),
    path("movies/<int:pk>/mark_as_watched/", mark_as_watched, name="mark-as-watched"),
    path(
        "movies/<int:pk>/remove_from_watchlist/",
        remove_from_watchlist,
        name="remove-from-watchlist"
    ),
    path(
        "movies/<int:pk>/watched/remove/",
        remove_from_watched,
        name="remove-from-watched"
    ),
    path("profile/", profile_view, name="profile"),
    path("profile/watchlist/", watchlist_view, name="watchlist"),
]
