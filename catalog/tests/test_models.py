from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from catalog.models import Director, Genre, Movie, UserMovie


class UserModelTests(TestCase):
    def test_create_user(self):
        username = "testuser"
        password = "testpassword123"

        user = get_user_model().objects.create_user(
            username=username,
            email="test@example.com",
            password=password,
        )

        self.assertEqual(user.username, username)
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password(password))

    def test_user_model_is_custom_user(self):
        user = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword123",
        )

        self.assertEqual(user.__class__.__name__, "User")


class GenreModelTests(TestCase):
    def test_genre_str(self):
        genre = Genre.objects.create(name="Drama")

        self.assertEqual(str(genre), "Drama")

    def test_genres_are_ordered_by_name(self):
        Genre.objects.create(name="Thriller")
        Genre.objects.create(name="Comedy")
        Genre.objects.create(name="Drama")

        genres = list(
            Genre.objects.values_list("name", flat=True)
        )

        self.assertEqual(
            genres,
            ["Comedy", "Drama", "Thriller"],
        )


class DirectorModelTests(TestCase):
    def test_director_str(self):
        director = Director.objects.create(
            first_name="Martin",
            last_name="Scorsese",
            year_of_birth=1942,
        )

        self.assertEqual(
            str(director),
            "Martin Scorsese",
        )

    def test_director_can_be_created_without_year_of_birth(self):
        director = Director.objects.create(
            first_name="David",
            last_name="Lynch",
        )

        self.assertIsNone(director.year_of_birth)

    def test_directors_are_ordered_by_last_name_then_first_name(self):
        Director.objects.create(
            first_name="Martin",
            last_name="Scorsese",
        )
        Director.objects.create(
            first_name="David",
            last_name="Lynch",
        )
        Director.objects.create(
            first_name="George",
            last_name="Miller",
        )
        Director.objects.create(
            first_name="Frank",
            last_name="Miller",
        )

        directors = list(
            Director.objects.values_list(
                "first_name",
                "last_name",
            )
        )

        self.assertEqual(
            directors,
            [
                ("David", "Lynch"),
                ("Frank", "Miller"),
                ("George", "Miller"),
                ("Martin", "Scorsese"),
            ],
        )


class MovieModelTests(TestCase):
    def setUp(self):
        self.director = Director.objects.create(
            first_name="Martin",
            last_name="Scorsese",
            year_of_birth=1942,
        )

        self.drama = Genre.objects.create(name="Drama")
        self.crime = Genre.objects.create(name="Crime")

        self.movie = Movie.objects.create(
            title="Taxi Driver",
            description="A lonely taxi driver in New York.",
            release_year=1976,
            director=self.director,
        )

    def test_movie_str(self):
        self.assertEqual(
            str(self.movie),
            "Taxi Driver",
        )

    def test_movie_can_have_genres(self):
        self.movie.genre.add(
            self.drama,
            self.crime,
        )

        self.assertEqual(
            self.movie.genre.count(),
            2,
        )

        self.assertIn(
            self.drama,
            self.movie.genre.all(),
        )
        self.assertIn(
            self.crime,
            self.movie.genre.all(),
        )

    def test_movie_can_be_created_without_poster(self):
        self.assertFalse(self.movie.poster)

    def test_movies_are_ordered_by_title(self):
        Movie.objects.create(
            title="Goodfellas",
            description="Crime movie.",
            release_year=1990,
            director=self.director,
        )

        Movie.objects.create(
            title="After Hours",
            description="Comedy movie.",
            release_year=1985,
            director=self.director,
        )

        titles = list(
            Movie.objects.values_list(
                "title",
                flat=True,
            )
        )

        self.assertEqual(
            titles,
            [
                "After Hours",
                "Goodfellas",
                "Taxi Driver",
            ],
        )

    def test_director_is_set_to_null_when_deleted(self):
        self.director.delete()

        self.movie.refresh_from_db()

        self.assertIsNone(
            self.movie.director
        )

    def test_movie_is_not_deleted_when_director_is_deleted(self):
        movie_id = self.movie.id

        self.director.delete()

        self.assertTrue(
            Movie.objects.filter(
                id=movie_id
            ).exists()
        )


class UserMovieModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword123",
        )

        self.director = Director.objects.create(
            first_name="Martin",
            last_name="Scorsese",
        )

        self.movie = Movie.objects.create(
            title="Taxi Driver",
            description="A lonely taxi driver in New York.",
            release_year=1976,
            director=self.director,
        )

    def test_user_movie_str(self):
        user_movie = UserMovie.objects.create(
            user=self.user,
            movie=self.movie,
        )

        self.assertEqual(
            str(user_movie),
            "testuser - Taxi Driver",
        )

    def test_watched_defaults_to_false(self):
        user_movie = UserMovie.objects.create(
            user=self.user,
            movie=self.movie,
        )

        self.assertFalse(
            user_movie.watched
        )

    def test_user_movie_can_be_marked_as_watched(self):
        user_movie = UserMovie.objects.create(
            user=self.user,
            movie=self.movie,
            watched=True,
        )

        self.assertTrue(
            user_movie.watched
        )

    def test_user_cannot_have_duplicate_movie_relation(self):
        UserMovie.objects.create(
            user=self.user,
            movie=self.movie,
        )

        with self.assertRaises(IntegrityError):
            UserMovie.objects.create(
                user=self.user,
                movie=self.movie,
            )

    def test_same_movie_can_belong_to_different_users(self):
        other_user = get_user_model().objects.create_user(
            username="otheruser",
            password="testpassword123",
        )

        UserMovie.objects.create(
            user=self.user,
            movie=self.movie,
        )

        UserMovie.objects.create(
            user=other_user,
            movie=self.movie,
        )

        self.assertEqual(
            UserMovie.objects.filter(
                movie=self.movie
            ).count(),
            2,
        )

    def test_same_user_can_have_different_movies(self):
        other_movie = Movie.objects.create(
            title="Goodfellas",
            description="Crime movie.",
            release_year=1990,
            director=self.director,
        )

        UserMovie.objects.create(
            user=self.user,
            movie=self.movie,
        )

        UserMovie.objects.create(
            user=self.user,
            movie=other_movie,
        )

        self.assertEqual(
            UserMovie.objects.filter(
                user=self.user
            ).count(),
            2,
        )

    def test_user_movie_is_deleted_when_user_is_deleted(self):
        user_movie = UserMovie.objects.create(
            user=self.user,
            movie=self.movie,
        )

        user_movie_id = user_movie.id

        self.user.delete()

        self.assertFalse(
            UserMovie.objects.filter(
                id=user_movie_id
            ).exists()
        )

    def test_user_movie_is_deleted_when_movie_is_deleted(self):
        user_movie = UserMovie.objects.create(
            user=self.user,
            movie=self.movie,
        )

        user_movie_id = user_movie.id

        self.movie.delete()

        self.assertFalse(
            UserMovie.objects.filter(
                id=user_movie_id
            ).exists()
        )
