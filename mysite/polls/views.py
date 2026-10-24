from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from mysite.polls.forms import VoteForm
from mysite.polls.models import Question


def index(request: HttpRequest) -> HttpResponse:
    questions = Question.objects.order_by("-published_date").all()[:5]
    context = {"questions": questions}

    return render(request=request, template_name="polls/index.html", context=context)


def detail(request: HttpRequest, question_id: int) -> HttpResponse:
    question = get_object_or_404(Question, id=question_id)
    form = VoteForm(data=request.POST or None, question=question)

    if form.is_valid():
        form.save()
        return redirect("polls:result", question.id)

    context = {"question": question, "form": form}
    return render(request=request, template_name="polls/detail.html", context=context)


def results(request: HttpRequest, question_id: int) -> HttpResponse:
    question = get_object_or_404(Question, id=question_id)
    context = {"question": question}
    return render(request=request, template_name="polls/result.html", context=context)
