from django import forms

from catalog.models import Director, Genre


class MovieSearchForm(forms.Form):
    query = forms.CharField(
        max_length=200,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search movies...",
                "class": "form-control",
            }
        ),
    )

    genre = forms.ModelChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        empty_label="All genres",
        label="",
        widget=forms.Select(
            attrs={"class": "form-select"}
        ),
    )

    director = forms.ModelChoiceField(
        queryset=Director.objects.all(),
        required=False,
        empty_label="All directors",
        label="",
        widget=forms.Select(
            attrs={"class": "form-select"}
        ),
    )
