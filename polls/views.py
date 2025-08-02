from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import Question, Choice

def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    choices = question.choice_set.all()
    total_votes = sum(choice.votes for choice in choices)
    
    # Debug: imprimir información
    print(f"DEBUG - Question ID: {question_id}")
    print(f"DEBUG - Total votes: {total_votes}")
    for choice in choices:
        print(f"DEBUG - {choice.choice_text}: {choice.votes} votes")
    
    # Calcular porcentajes
    choices_with_percentage = []
    for choice in choices:
        if total_votes > 0:
            percentage = (choice.votes / total_votes) * 100
        else:
            percentage = 0
        choices_with_percentage.append({
            'choice': choice,
            'percentage': round(percentage, 1)
        })
    
    context = {
        'question': question,
        'choices_with_percentage': choices_with_percentage,
        'total_votes': total_votes
    }
    return render(request, 'polls/results.html', context)

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "No seleccionaste una opción válida.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        messages.success(request, '¡Tu voto ha sido registrado correctamente!')
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
