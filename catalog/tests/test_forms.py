from django.contrib.auth import get_user_model
from django.test import TestCase

from catalog.forms import DirectorSearchForm, MovieSearchForm, SignUpForm
from catalog.models import Director, Genre


class MovieSearchFormTests(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Drama")

        self.director = Director.objects.create(
            first_name="Martin",
            last_name="Scorsese",
            year_of_birth=1942,
        )

    def test_form_is_valid_with_all_fields(self):
        form_data = {
            "query": "Taxi Driver",
            "genre": self.genre.id,
            "director": self.director.id,
        }

        form = MovieSearchForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["query"], "Taxi Driver")
        self.assertEqual(form.cleaned_data["genre"], self.genre)
        self.assertEqual(form.cleaned_data["director"], self.director)

    def test_form_is_valid_with_empty_fields(self):
        form = MovieSearchForm(data={})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["query"], "")
        self.assertIsNone(form.cleaned_data["genre"])
        self.assertIsNone(form.cleaned_data["director"])

    def test_query_max_length(self):
        form = MovieSearchForm(
            data={"query": "a" * 201}
        )

        self.assertFalse(form.is_valid())
        self.assertIn("query", form.errors)

    def test_invalid_genre(self):
        form = MovieSearchForm(
            data={"genre": 99999}
        )

        self.assertFalse(form.is_valid())
        self.assertIn("genre", form.errors)

    def test_invalid_director(self):
        form = MovieSearchForm(
            data={"director": 99999}
        )

        self.assertFalse(form.is_valid())
        self.assertIn("director", form.errors)

    def test_genre_queryset_contains_existing_genres(self):
        form = MovieSearchForm()

        self.assertIn(
            self.genre,
            form.fields["genre"].queryset,
        )

    def test_director_queryset_contains_existing_directors(self):
        form = MovieSearchForm()

        self.assertIn(
            self.director,
            form.fields["director"].queryset,
        )

    def test_query_widget_attributes(self):
        form = MovieSearchForm()

        widget = form.fields["query"].widget

        self.assertEqual(
            widget.attrs["placeholder"],
            "Search movies...",
        )
        self.assertEqual(
            widget.attrs["class"],
            "form-control",
        )

    def test_genre_and_director_widgets_have_form_select_class(self):
        form = MovieSearchForm()

        self.assertEqual(
            form.fields["genre"].widget.attrs["class"],
            "form-select",
        )
        self.assertEqual(
            form.fields["director"].widget.attrs["class"],
            "form-select",
        )


class DirectorSearchFormTests(TestCase):
    def test_form_is_valid_with_query(self):
        form = DirectorSearchForm(
            data={"query": "Scorsese"}
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["query"],
            "Scorsese",
        )

    def test_form_is_valid_without_query(self):
        form = DirectorSearchForm(data={})

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["query"],
            "",
        )

    def test_query_max_length(self):
        form = DirectorSearchForm(
            data={"query": "a" * 201}
        )

        self.assertFalse(form.is_valid())
        self.assertIn("query", form.errors)

    def test_query_widget_attributes(self):
        form = DirectorSearchForm()

        widget = form.fields["query"].widget

        self.assertEqual(
            widget.attrs["placeholder"],
            "Search directors...",
        )
        self.assertEqual(
            widget.attrs["class"],
            "form-control",
        )


class SignUpFormTests(TestCase):
    def test_form_is_valid_with_valid_data(self):
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }

        form = SignUpForm(data=form_data)

        self.assertTrue(form.is_valid())

    def test_email_is_required(self):
        form_data = {
            "username": "testuser",
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }

        form = SignUpForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_invalid_email(self):
        form_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }

        form = SignUpForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_passwords_must_match(self):
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "StrongPassword123!",
            "password2": "DifferentPassword123!",
        }

        form = SignUpForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_username_must_be_unique(self):
        get_user_model().objects.create_user(
            username="testuser",
            email="existing@example.com",
            password="StrongPassword123!",
        )

        form_data = {
            "username": "testuser",
            "email": "new@example.com",
            "password1": "AnotherPassword123!",
            "password2": "AnotherPassword123!",
        }

        form = SignUpForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_form_creates_user(self):
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }

        form = SignUpForm(data=form_data)

        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(
            user.check_password("StrongPassword123!")
        )

    def test_password_is_not_saved_as_plain_text(self):
        form_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }

        form = SignUpForm(data=form_data)

        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertNotEqual(
            user.password,
            "StrongPassword123!",
        )

    def test_signup_form_uses_custom_user_model(self):
        form = SignUpForm()

        self.assertEqual(
            form._meta.model,
            get_user_model(),
        )
