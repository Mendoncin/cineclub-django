from django.shortcuts import render
from catalog.models import Movie, Genre, Director
from django.views import generic

# Create your views here.


def index(request):
    num_movies = Movie.objects.count()
    num_directors = Director.objects.count()
    num_genres = Genre.objects.count()

    context = {
        "num_movies": num_movies,
        "num_directors": num_directors,
        "num_genres": num_genres,
    }
    return render(request, "catalog/home.html", context)


class MoviesListView(generic.ListView):
    model = Movie
    template_name = "catalog/movie_list.html"
    context_object_name = "movies"


class MovieDetailView(generic.DetailView):
    model = Movie
    template_name = "catalog/movie_detail.html"
    context_object_name = "movie"
