from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.models import Director, Genre, Movie, UserMovie


class BaseViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )

        self.other_user = get_user_model().objects.create_user(
            username="otheruser",
            password="testpassword123",
        )

        self.genre = Genre.objects.create(
            name="Drama"
        )

        self.other_genre = Genre.objects.create(
            name="Crime"
        )

        self.director = Director.objects.create(
            first_name="Martin",
            last_name="Scorsese",
            year_of_birth=1942,
        )

        self.other_director = Director.objects.create(
            first_name="Christopher",
            last_name="Nolan",
            year_of_birth=1970,
        )

        self.movie = Movie.objects.create(
            title="Taxi Driver",
            description="A lonely taxi driver in New York.",
            release_year=1976,
            director=self.director,
        )
        self.movie.genre.add(self.genre)

        self.other_movie = Movie.objects.create(
            title="Inception",
            description="A science fiction movie.",
            release_year=2010,
            director=self.other_director,
        )
        self.other_movie.genre.add(self.other_genre)


class LoginRequiredViewTests(BaseViewTest):
    def test_index_requires_login(self):
        url = reverse("catalog:index")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_profile_requires_login(self):
        url = reverse("catalog:profile")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_watchlist_requires_login(self):
        url = reverse("catalog:watchlist")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_movie_list_requires_login(self):
        url = reverse("catalog:movie-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_movie_detail_requires_login(self):
        url = reverse(
            "catalog:movie-detail",
            args=[self.movie.id],
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_director_list_requires_login(self):
        url = reverse("catalog:director-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_director_detail_requires_login(self):
        url = reverse(
            "catalog:director-detail",
            args=[self.director.id],
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_genre_list_requires_login(self):
        url = reverse("catalog:genre-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)


class IndexViewTests(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_index_uses_correct_template(self):
        response = self.client.get(
            reverse("catalog:index")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "catalog/home.html",
        )

    def test_index_contains_model_counts(self):
        response = self.client.get(
            reverse("catalog:index")
        )

        self.assertEqual(
            response.context["num_movies"],
            2,
        )
        self.assertEqual(
            response.context["num_directors"],
            2,
        )
        self.assertEqual(
            response.context["num_genres"],
            2,
        )


class ProfileViewTests(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_profile_uses_correct_template(self):
        response = self.client.get(
            reverse("catalog:profile")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "catalog/profile.html",
        )

    def test_profile_contains_watched_movies(self):
        watched = UserMovie.objects.create(
            user=self.user,
            movie=self.movie,
            watched=True,
        )

        response = self.client.get(
            reverse("catalog:profile")
        )

        self.assertIn(
            watched,
            response.context["watched_movies"],
        )

    def test_profile_does_not_contain_watchlist_movies(self):
        watchlist_movie = UserMovie.objects.create(
            user=self.user,
            movie=self.movie,
            watched=False,
        )

        response = self.client.get(
            reverse("catalog:profile")
        )

        self.assertNotIn(
            watchlist_movie,
            response.context["watched_movies"],
        )

    def test_profile_does_not_show_other_users_movies(self):
        other_user_movie = UserMovie.objects.create(
            user=self.other_user,
            movie=self.movie,
            watched=True,
        )

        response = self.client.get(
            reverse("catalog:profile")
        )

        self.assertNotIn(
            other_user_movie,
            response.context["watched_movies"],
        )


class WatchlistViewTests(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_watchlist_uses_correct_template(self):
        response = self.client.get(
            reverse("catalog:watchlist")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "catalog/watchlist.html",
        )

    def test_watchlist_contains_unwatched_movies(self):
        watchlist_movie = UserMovie.objects.create(
            user=self.user,
            movie=self.movie,
            watched=False,
        )

        response = self.client.get(
            reverse("catalog:watchlist")
        )

        self.assertIn(
            watchlist_movie,
            response.context["watchlist"],
        )

    def test_watchlist_does_not_contain_watched_movies(self):
        watched_movie = UserMovie.objects.create(
            user=self.user,
            movie=self.movie,
            watched=True,
        )

        response = self.client.get(
            reverse("catalog:watchlist")
        )

        self.assertNotIn(
            watched_movie,
            response.context["watchlist"],
        )

    def test_watchlist_does_not_show_other_users_movies(self):
        other_user_movie = UserMovie.objects.create(
            user=self.other_user,
            movie=self.movie,
            watched=False,
        )

        response = self.client.get(
            reverse("catalog:watchlist")
        )

        self.assertNotIn(
            other_user_movie,
            response.context["watchlist"],
        )


class WatchlistActionsTests(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_add_movie_to_watchlist(self):
        url = reverse(
            "catalog:add-to-watchlist",
            args=[self.movie.id],
        )

        response = self.client.post(url)

        user_movie = UserMovie.objects.get(
            user=self.user,
            movie=self.movie,
        )

        self.assertFalse(user_movie.watched)

        self.assertRedirects(
            response,
            reverse(
                "catalog:movie-detail",
                args=[self.movie.id],
            ),
        )

    def test_add_to_watchlist_changes_watched_movie_to_unwatched(self):
        user_movie = UserMovie.objects.create(
            user=self.user,
            movie=self.movie,
            watched=True,
        )

        url = reverse(
            "catalog:add-to-watchlist",
            args=[self.movie.id],
        )
        self.client.post(url)

        user_movie.refresh_from_db()

        self.assertFalse(user_movie.watched)

    def test_mark_movie_as_watched(self):
        url = reverse(
            "catalog:mark-as-watched",
            args=[self.movie.id],
        )

        response = self.client.post(url)

        user_movie = UserMovie.objects.get(
            user=self.user,
            movie=self.movie,
        )

        self.assertTrue(user_movie.watched)

        self.assertRedirects(
            response,
            reverse(
                "catalog:movie-detail",
                args=[self.movie.id],
            ),
        )

    def test_mark_as_watched_updates_existing_watchlist_entry(self):
        user_movie = UserMovie.objects.create(
            user=self.user,
            movie=self.movie,
            watched=False,
        )

        url = reverse(
            "catalog:mark-as-watched",
            args=[self.movie.id],
        )
        self.client.post(url)

        user_movie.refresh_from_db()

        self.assertTrue(user_movie.watched)

    def test_remove_from_watchlist(self):
        UserMovie.objects.create(
            user=self.user,
            movie=self.movie,
            watched=False,
        )

        url = reverse(
            "catalog:remove-from-watchlist",
            args=[self.movie.id],
        )

        response = self.client.post(url)

        self.assertFalse(
            UserMovie.objects.filter(
                user=self.user,
                movie=self.movie,
            ).exists()
        )

        self.assertRedirects(
            response,
            reverse(
                "catalog:movie-detail",
                args=[self.movie.id],
            ),
        )

    def test_remove_from_watchlist_does_not_remove_watched_movie(self):
        UserMovie.objects.create(
            user=self.user,
            movie=self.movie,
            watched=True,
        )

        url = reverse(
            "catalog:remove-from-watchlist",
            args=[self.movie.id],
        )
        self.client.post(url)

        self.assertTrue(
            UserMovie.objects.filter(
                user=self.user,
                movie=self.movie,
                watched=True,
            ).exists()
        )

    def test_remove_from_watched(self):
        UserMovie.objects.create(
            user=self.user,
            movie=self.movie,
            watched=True,
        )

        url = reverse(
            "catalog:remove-from-watched",
            args=[self.movie.id],
        )

        response = self.client.post(url)

        self.assertFalse(
            UserMovie.objects.filter(
                user=self.user,
                movie=self.movie,
            ).exists()
        )

        self.assertRedirects(
            response,
            reverse(
                "catalog:movie-detail",
                args=[self.movie.id],
            ),
        )

    def test_remove_from_watched_does_not_remove_watchlist_movie(self):
        UserMovie.objects.create(
            user=self.user,
            movie=self.movie,
            watched=False,
        )

        url = reverse(
            "catalog:remove-from-watched",
            args=[self.movie.id],
        )
        self.client.post(url)

        self.assertTrue(
            UserMovie.objects.filter(
                user=self.user,
                movie=self.movie,
                watched=False,
            ).exists()
        )

    def test_watchlist_actions_do_not_affect_other_users(self):
        UserMovie.objects.create(
            user=self.other_user,
            movie=self.movie,
            watched=False,
        )

        url = reverse(
            "catalog:remove-from-watchlist",
            args=[self.movie.id],
        )
        self.client.post(url)

        self.assertTrue(
            UserMovie.objects.filter(
                user=self.other_user,
                movie=self.movie,
            ).exists()
        )

    def test_add_to_watchlist_requires_post(self):
        url = reverse(
            "catalog:add-to-watchlist",
            args=[self.movie.id],
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 405)

    def test_mark_as_watched_requires_post(self):
        url = reverse(
            "catalog:mark-as-watched",
            args=[self.movie.id],
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 405)

    def test_remove_from_watchlist_requires_post(self):
        url = reverse(
            "catalog:remove-from-watchlist",
            args=[self.movie.id],
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 405)

    def test_remove_from_watched_requires_post(self):
        url = reverse(
            "catalog:remove-from-watched",
            args=[self.movie.id],
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 405)

    def test_watchlist_action_returns_404_for_invalid_movie(self):
        url = reverse(
            "catalog:add-to-watchlist",
            args=[99999],
        )

        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)


class MovieListViewTests(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_movie_list_uses_correct_template(self):
        response = self.client.get(
            reverse("catalog:movie-list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "catalog/movie_list.html",
        )

    def test_movie_list_contains_movies(self):
        response = self.client.get(
            reverse("catalog:movie-list")
        )

        self.assertIn(
            self.movie,
            response.context["movies"],
        )
        self.assertIn(
            self.other_movie,
            response.context["movies"],
        )

    def test_search_movies_by_title(self):
        response = self.client.get(
            reverse("catalog:movie-list"),
            {"query": "Taxi"},
        )

        self.assertIn(
            self.movie,
            response.context["movies"],
        )
        self.assertNotIn(
            self.other_movie,
            response.context["movies"],
        )

    def test_movie_search_is_case_insensitive(self):
        response = self.client.get(
            reverse("catalog:movie-list"),
            {"query": "taxi"},
        )

        self.assertIn(
            self.movie,
            response.context["movies"],
        )

    def test_filter_movies_by_genre(self):
        response = self.client.get(
            reverse("catalog:movie-list"),
            {"genre": self.genre.id},
        )

        self.assertIn(
            self.movie,
            response.context["movies"],
        )
        self.assertNotIn(
            self.other_movie,
            response.context["movies"],
        )

    def test_filter_movies_by_director(self):
        response = self.client.get(
            reverse("catalog:movie-list"),
            {"director": self.director.id},
        )

        self.assertIn(
            self.movie,
            response.context["movies"],
        )
        self.assertNotIn(
            self.other_movie,
            response.context["movies"],
        )

    def test_combined_movie_filters(self):
        response = self.client.get(
            reverse("catalog:movie-list"),
            {
                "query": "Taxi",
                "genre": self.genre.id,
                "director": self.director.id,
            },
        )

        self.assertEqual(
            list(response.context["movies"]),
            [self.movie],
        )

    def test_movie_list_contains_search_form(self):
        response = self.client.get(
            reverse("catalog:movie-list")
        )

        self.assertIn(
            "search_form",
            response.context,
        )

    def test_query_string_excludes_page_parameter(self):
        response = self.client.get(
            reverse("catalog:movie-list"),
            {
                "query": "Taxi",
                "genre": self.genre.id,
                "page": 1,
            },
        )

        query_string = response.context[
            "query_string"
        ]

        self.assertIn(
            "query=Taxi",
            query_string,
        )
        self.assertIn(
            f"genre={self.genre.id}",
            query_string,
        )
        self.assertNotIn(
            "page=",
            query_string,
        )

    def test_movie_list_is_paginated_by_12(self):
        for index in range(12):
            Movie.objects.create(
                title=f"Movie {index}",
                description="Test description",
                release_year=2000 + index,
                director=self.director,
            )

        response = self.client.get(
            reverse("catalog:movie-list")
        )

        self.assertTrue(
            response.context["is_paginated"]
        )
        self.assertEqual(
            len(response.context["movies"]),
            12,
        )


class MovieDetailViewTests(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_movie_detail_uses_correct_template(self):
        response = self.client.get(
            reverse(
                "catalog:movie-detail",
                args=[self.movie.id],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "catalog/movie_detail.html",
        )

    def test_movie_detail_contains_correct_movie(self):
        response = self.client.get(
            reverse(
                "catalog:movie-detail",
                args=[self.movie.id],
            )
        )

        self.assertEqual(
            response.context["movie"],
            self.movie,
        )

    def test_movie_detail_contains_user_movie_relation(self):
        user_movie = UserMovie.objects.create(
            user=self.user,
            movie=self.movie,
            watched=True,
        )

        response = self.client.get(
            reverse(
                "catalog:movie-detail",
                args=[self.movie.id],
            )
        )

        self.assertEqual(
            response.context["user_movie"],
            user_movie,
        )

    def test_movie_detail_user_movie_is_none_when_no_relation_exists(self):
        response = self.client.get(
            reverse(
                "catalog:movie-detail",
                args=[self.movie.id],
            )
        )

        self.assertIsNone(
            response.context["user_movie"]
        )

    def test_movie_detail_does_not_use_other_users_relation(self):
        UserMovie.objects.create(
            user=self.other_user,
            movie=self.movie,
            watched=True,
        )

        response = self.client.get(
            reverse(
                "catalog:movie-detail",
                args=[self.movie.id],
            )
        )

        self.assertIsNone(
            response.context["user_movie"]
        )

    def test_movie_detail_returns_404_for_invalid_movie(self):
        response = self.client.get(
            reverse(
                "catalog:movie-detail",
                args=[99999],
            )
        )

        self.assertEqual(response.status_code, 404)


class DirectorListViewTests(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_director_list_uses_correct_template(self):
        response = self.client.get(
            reverse("catalog:director-list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "catalog/director_list.html",
        )

    def test_director_list_contains_directors(self):
        response = self.client.get(
            reverse("catalog:director-list")
        )

        self.assertIn(
            self.director,
            response.context["directors"],
        )
        self.assertIn(
            self.other_director,
            response.context["directors"],
        )

    def test_search_director_by_first_name(self):
        response = self.client.get(
            reverse("catalog:director-list"),
            {"query": "Martin"},
        )

        self.assertIn(
            self.director,
            response.context["directors"],
        )
        self.assertNotIn(
            self.other_director,
            response.context["directors"],
        )

    def test_search_director_by_last_name(self):
        response = self.client.get(
            reverse("catalog:director-list"),
            {"query": "Scorsese"},
        )

        self.assertIn(
            self.director,
            response.context["directors"],
        )
        self.assertNotIn(
            self.other_director,
            response.context["directors"],
        )

    def test_search_director_by_full_name(self):
        response = self.client.get(
            reverse("catalog:director-list"),
            {"query": "Martin Scorsese"},
        )

        self.assertIn(
            self.director,
            response.context["directors"],
        )
        self.assertNotIn(
            self.other_director,
            response.context["directors"],
        )

    def test_director_has_movie_count(self):
        response = self.client.get(
            reverse("catalog:director-list")
        )

        directors = response.context[
            "directors"
        ]

        martin = next(
            director
            for director in directors
            if director == self.director
        )

        self.assertEqual(
            martin.num_movies,
            1,
        )

    def test_directors_are_ordered_by_first_name_then_last_name(self):
        response = self.client.get(
            reverse("catalog:director-list")
        )

        directors = list(
            response.context["directors"]
        )

        self.assertEqual(
            directors,
            sorted(
                directors,
                key=lambda director: (
                    director.first_name,
                    director.last_name,
                ),
            ),
        )

    def test_director_list_contains_search_form(self):
        response = self.client.get(
            reverse("catalog:director-list")
        )

        self.assertIn(
            "search_form",
            response.context,
        )


class DirectorDetailViewTests(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_director_detail_uses_correct_template(self):
        response = self.client.get(
            reverse(
                "catalog:director-detail",
                args=[self.director.id],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "catalog/director_detail.html",
        )

    def test_director_detail_contains_correct_director(self):
        response = self.client.get(
            reverse(
                "catalog:director-detail",
                args=[self.director.id],
            )
        )

        self.assertEqual(
            response.context["director"],
            self.director,
        )

    def test_director_detail_returns_404_for_invalid_director(self):
        response = self.client.get(
            reverse(
                "catalog:director-detail",
                args=[99999],
            )
        )

        self.assertEqual(response.status_code, 404)


class GenreListViewTests(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_genre_list_uses_correct_template(self):
        response = self.client.get(
            reverse("catalog:genre-list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "catalog/genre_list.html",
        )

    def test_genre_list_contains_genres(self):
        response = self.client.get(
            reverse("catalog:genre-list")
        )

        self.assertIn(
            self.genre,
            response.context["genres"],
        )
        self.assertIn(
            self.other_genre,
            response.context["genres"],
        )

    def test_genre_has_movie_count(self):
        response = self.client.get(
            reverse("catalog:genre-list")
        )

        genres = response.context["genres"]

        drama = next(
            genre
            for genre in genres
            if genre == self.genre
        )

        self.assertEqual(
            drama.num_movies,
            1,
        )


class SignUpViewTests(TestCase):
    def test_signup_page_is_public(self):
        response = self.client.get(
            reverse("catalog:signup")
        )

        self.assertEqual(response.status_code, 200)

    def test_signup_uses_correct_template(self):
        response = self.client.get(
            reverse("catalog:signup")
        )

        self.assertTemplateUsed(
            response,
            "registration/signup.html",
        )

    def test_signup_creates_user(self):
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }

        response = self.client.post(
            reverse("catalog:signup"),
            form_data,
        )

        self.assertTrue(
            get_user_model().objects.filter(
                username="newuser"
            ).exists()
        )

        self.assertRedirects(
            response,
            reverse("login"),
        )

    def test_signup_does_not_create_user_with_invalid_data(self):
        form_data = {
            "username": "newuser",
            "email": "invalid-email",
            "password1": "StrongPassword123!",
            "password2": "DifferentPassword123!",
        }

        response = self.client.post(
            reverse("catalog:signup"),
            form_data,
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            get_user_model().objects.filter(
                username="newuser"
            ).exists()
        )
