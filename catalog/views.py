from multiprocessing import context

from django.db.models.aggregates import Count
from django.shortcuts import render
from catalog.models import Movie, Genre, Director
from django.views import generic
from catalog.forms import MovieSearchForm, DirectorSearchForm
from django.db.models import Q

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
    paginate_by = 12

    def get_queryset(self):
        queryset = Movie.objects.select_related(
            "director"
        ).prefetch_related(
            "genre"
        )

        form = MovieSearchForm(self.request.GET)

        if form.is_valid():
            query = form.cleaned_data["query"]
            genre = form.cleaned_data["genre"]
            director = form.cleaned_data["director"]

            if query:
                queryset = queryset.filter(
                    title__icontains=query
                )

            if genre:
                queryset = queryset.filter(
                    genre=genre
                )

            if director:
                queryset = queryset.filter(
                    director=director
                )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = MovieSearchForm(
            self.request.GET
        )
        query_params = self.request.GET.copy()
        query_params.pop("page", None)
        context["query_string"] = query_params.urlencode()

        return context


class MovieDetailView(generic.DetailView):
    model = Movie
    template_name = "catalog/movie_detail.html"
    context_object_name = "movie"


class DirectorListView(generic.ListView):
    model = Director
    template_name = "catalog/director_list.html"
    context_object_name = "directors"

    def get_queryset(self):
        queryset = Director.objects.annotate(
            num_movies=Count("movie")
        )

        form = DirectorSearchForm(self.request.GET)

        if form.is_valid():
            query = form.cleaned_data["query"]

            if query:
                terms = query.split()

                for term in terms:
                    queryset = queryset.filter(
                        Q(first_name__icontains=term)
                        | Q(last_name__icontains=term)
                    )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = DirectorSearchForm(
            self.request.GET
        )
        return context


class DirectorDetailView(generic.DetailView):
    model = Director
    template_name = "catalog/director_detail.html"
    context_object_name = "director"


class GenreListView(generic.ListView):
    model = Genre
    template_name = "catalog/genre_list.html"
    context_object_name = "genres"

    def get_queryset(self):
        return Genre.objects.annotate(
            num_movies=Count("movie")
        )
