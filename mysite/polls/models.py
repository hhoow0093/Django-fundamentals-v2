# Create your models here.
import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    published_date = models.DateTimeField(verbose_name="Date published", auto_now_add=True)

    def was_published_recently(self) -> bool:
        """checks if it was published within 24 hours.
        If more than 24 hours, return False otherwise True."""
        return self.published_date >= timezone.now() - datetime.timedelta(days=1)

    def __str__(self) -> str:
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(
        to="polls.Question", related_name="choices", on_delete=models.CASCADE
    )
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.choice_text
