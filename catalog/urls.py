from django.urls import path
from catalog.views import index, MoviesListView, MovieDetailView

app_name = "catalog"

urlpatterns = [
    path("", index, name="index"),
    path("movies/", MoviesListView.as_view(), name="movie-list"),
    path("movies/<int:pk>/", MovieDetailView.as_view(), name="movie-detail"),
]
