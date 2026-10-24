from typing import Any

from django import forms

from mysite.polls.models import Choice, Question


class VoteForm(forms.Form):
    choices = forms.ModelChoiceField(
        queryset=Choice.objects.none(), widget=forms.RadioSelect, required=True
    )

    def __init__(self, question: Question, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.question = question
        self.fields["choices"].queryset = self.question.choices.all()  # type: ignore

    def save(self) -> Choice:
        choice: Choice = self.cleaned_data["choices"]
        choice.votes += 1
        choice.save()
        return choice
