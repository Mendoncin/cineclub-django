from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from catalog.models import Director, Genre, Movie, UserMovie


class AdminSiteTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="adminpassword",
        )
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="testuser@test.com",
            password="testpassword",
            first_name="Test",
            last_name="User",
        )

        self.genre = Genre.objects.create(
            name="Drama"
        )

        self.director = Director.objects.create(
            first_name="Martin",
            last_name="Scorsese",
            year_of_birth=1942,
        )

        self.movie = Movie.objects.create(
            title="Taxi Driver",
            description="A lonely taxi driver in New York.",
            release_year=1976,
            director=self.director,
        )
        self.movie.genre.add(self.genre)

        self.user_movie = UserMovie.objects.create(
            user=self.user,
            movie=self.movie,
            watched=True,
        )

    def test_models_are_registered_in_admin(self):
        """Test that all catalog models are registered in the admin site."""
        registered_models = admin.site._registry

        self.assertIn(get_user_model(), registered_models)
        self.assertIn(Genre, registered_models)
        self.assertIn(Director, registered_models)
        self.assertIn(Movie, registered_models)
        self.assertIn(UserMovie, registered_models)

    def test_user_list_display(self):
        """Test that user information is displayed in the admin list view."""
        url = reverse("admin:catalog_user_changelist")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user.first_name)
        self.assertContains(response, self.user.last_name)

    def test_user_detail_view(self):
        """Test that user information is displayed in the admin detail view."""
        url = reverse(
            "admin:catalog_user_change",
            args=[self.user.id]
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.user.email)

    def test_genre_list_display(self):
        """Test that genres are displayed in the admin list view."""
        url = reverse("admin:catalog_genre_changelist")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.genre.name)

    def test_genre_search(self):
        """Test searching genres by name in the admin."""
        Genre.objects.create(name="Comedy")

        url = reverse("admin:catalog_genre_changelist")
        response = self.client.get(url, {"q": "Drama"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Drama")
        self.assertNotContains(response, "Comedy")

    def test_director_list_display(self):
        """Test that director fields are displayed in the admin list view."""
        url = reverse("admin:catalog_director_changelist")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.director.first_name)
        self.assertContains(response, self.director.last_name)
        self.assertContains(response, self.director.year_of_birth)

    def test_director_search_by_last_name(self):
        """Test searching directors by last name."""
        Director.objects.create(
            first_name="Christopher",
            last_name="Nolan",
            year_of_birth=1970,
        )

        url = reverse("admin:catalog_director_changelist")
        response = self.client.get(url, {"q": "Scorsese"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Scorsese")
        self.assertNotContains(response, "Nolan")

    def test_movie_list_display(self):
        """Test that movie fields are displayed in the admin list view."""
        url = reverse("admin:catalog_movie_changelist")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.movie.title)
        self.assertContains(response, str(self.movie.release_year))
        self.assertContains(response, str(self.movie.director))

    def test_movie_search_by_title(self):
        """Test searching movies by title."""
        other_movie = Movie.objects.create(
            title="Inception",
            description="A science fiction movie.",
            release_year=2010,
            director=self.director,
        )

        url = reverse("admin:catalog_movie_changelist")
        response = self.client.get(url, {"q": "Taxi Driver"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.movie.title)
        self.assertNotContains(response, other_movie.title)

    def test_movie_search_by_director_name(self):
        """Test searching movies by director name."""
        other_director = Director.objects.create(
            first_name="Christopher",
            last_name="Nolan",
            year_of_birth=1970,
        )

        other_movie = Movie.objects.create(
            title="Inception",
            description="A science fiction movie.",
            release_year=2010,
            director=other_director,
        )

        url = reverse("admin:catalog_movie_changelist")
        response = self.client.get(url, {"q": "Scorsese"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.movie.title)
        self.assertNotContains(response, other_movie.title)

    def test_user_movie_list_display(self):
        """Test that user-movie information is displayed in admin."""
        url = reverse("admin:catalog_usermovie_changelist")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.movie.title)

    def test_user_movie_search_by_username(self):
        """Test searching UserMovie records by username."""
        other_user = get_user_model().objects.create_user(
            username="otheruser",
            password="password",
        )

        UserMovie.objects.create(
            user=other_user,
            movie=self.movie,
            watched=False,
        )

        url = reverse("admin:catalog_usermovie_changelist")
        response = self.client.get(url, {"q": self.user.username})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertNotContains(response, other_user.username)

    def test_user_movie_search_by_movie_title(self):
        """Test searching UserMovie records by movie title."""
        other_movie = Movie.objects.create(
            title="Goodfellas",
            description="A crime movie.",
            release_year=1990,
            director=self.director,
        )

        UserMovie.objects.create(
            user=self.user,
            movie=other_movie,
            watched=False,
        )

        url = reverse("admin:catalog_usermovie_changelist")
        response = self.client.get(url, {"q": "Taxi Driver"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Taxi Driver")
        self.assertNotContains(response, "Goodfellas")

    def test_admin_requires_authentication(self):
        """Test that unauthenticated users cannot access the admin."""
        self.client.logout()

        url = reverse("admin:catalog_movie_changelist")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin:login"), response.url)
