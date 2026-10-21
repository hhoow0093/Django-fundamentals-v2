import datetime

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from mysite.polls.models import Question


class TestHelloWorld(TestCase):
    def setUp(self):
        self.question = Question.objects.create(question_text="What is your name")
        self.client = Client()

    def test_question(self) -> None:
        # question published now
        self.question = Question.objects.create(question_text="What is your name")
        self.assertTrue(self.question.was_published_recently())
        # question published in the future
        self.question.published_date = timezone.now() + datetime.timedelta(days=10)
        self.question.save()
        self.assertFalse(self.question.was_published_recently())
        # question older than 1 day
        self.question.published_date = timezone.now() - datetime.timedelta(days=10)
        self.question.save()
        self.assertFalse(self.question.was_published_recently())

    def test_client_index(self) -> None:
        # past question
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["questions"], [self.question])
        # future question
        self.question.published_date = timezone.now() + datetime.timedelta(days=10)
        self.question.save()
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["questions"], [])
        # test future and past (only past will be shown)
        question = Question.objects.create(question_text="Who is the president ot Indonesia")
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["questions"], [question])
        # should display multiple questions
        question_2 = Question.objects.create(question_text="Who is the president ot India")
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["questions"], [question_2, question]
        )  # sort by moct recent

    def test_client_detail(self) -> None:
        # past question
        response = self.client.get(reverse("polls:detail", args=[self.question.id]))
        self.assertEqual(response.status_code, 200)
        # future question
        self.question.published_date = timezone.now() + datetime.timedelta(days=10)
        self.question.save()
        response = self.client.get(reverse("polls:detail", args=[self.question.id]))
        self.assertEqual(response.status_code, 404)
