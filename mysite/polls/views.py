from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from mysite.polls.models import Question


def index(request: HttpRequest) -> HttpResponse:
    questions = Question.objects.order_by("-published_date").all()[:5]
    context = {"questions": questions}

    return render(request=request, template_name="polls/index.html", context=context)


def detail(request: HttpRequest, question_id: int) -> HttpResponse:
    question = get_object_or_404(Question, id=question_id)
    context = {"question": question}
    return render(request=request, template_name="polls/detail.html", context=context)


def results(request: HttpRequest, question_id: int) -> HttpResponse:
    return HttpResponse(f"You're looking at the results of question {question_id}.")


def vote(request: HttpRequest, question_id: int) -> HttpResponse:
    return HttpResponse(f"You are voting on question {question_id}.")
