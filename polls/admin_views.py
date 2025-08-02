from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.db import models
from .models import Question, Choice

def admin_dashboard(request):
    """Vista personalizada del dashboard administrativo"""
    questions = Question.objects.all().order_by('-pub_date')
    
    # Estadísticas generales
    total_questions = questions.count()
    total_votes = 0
    for q in questions:
        for choice in q.choice_set.all():
            total_votes += choice.votes
    
    # Verificar si el usuario es administrador
    is_admin = request.user.is_authenticated and request.user.is_staff
    
    context = {
        'questions': questions,
        'total_questions': total_questions,
        'total_votes': total_votes,
        'is_admin': is_admin,
        'user': request.user,
    }
    return render(request, 'admin/dashboard.html', context)
    
    context = {
        'questions': questions,
        'total_questions': total_questions,
        'total_votes': total_votes,
    }
    return render(request, 'admin/dashboard.html', context)

@login_required
def create_question(request):
    """Vista para crear nuevas preguntas"""
    # Verificar si el usuario es staff
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('polls:admin_dashboard')
    
    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        choices = [
            request.POST.get('choice1'),
            request.POST.get('choice2'),
            request.POST.get('choice3'),
            request.POST.get('choice4'),
        ]
        
        if question_text:
            # Crear la pregunta
            question = Question.objects.create(
                question_text=question_text,
                pub_date=timezone.now()
            )
            
            # Crear las opciones
            for choice_text in choices:
                if choice_text:
                    Choice.objects.create(
                        question=question,
                        choice_text=choice_text,
                        votes=0
                    )
            
            messages.success(request, f'Encuesta "{question_text}" creada exitosamente!')
            return redirect('polls:admin_dashboard')
    
    return render(request, 'admin/create_question.html')

@login_required
def edit_question(request, question_id):
    """Vista para editar preguntas existentes"""
    # Verificar si el usuario es staff
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('polls:admin_dashboard')
    
    question = get_object_or_404(Question, pk=question_id)
    choices = question.choice_set.all()
    
    if request.method == 'POST':
        question.question_text = request.POST.get('question_text')
        question.save()
        
        # Actualizar opciones
        for choice in choices:
            choice_text = request.POST.get(f'choice_{choice.id}')
            if choice_text:
                choice.choice_text = choice_text
                choice.save()
        
        messages.success(request, 'Encuesta actualizada exitosamente!')
        return redirect('polls:admin_dashboard')
    
    context = {
        'question': question,
        'choices': choices,
    }
    return render(request, 'admin/edit_question.html', context)

@login_required
def delete_question(request, question_id):
    """Vista para eliminar preguntas"""
    # Verificar si el usuario es staff
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('polls:admin_dashboard')
    
    question = get_object_or_404(Question, pk=question_id)
    
    if request.method == 'POST':
        question_text = question.question_text
        question.delete()
        messages.success(request, f'Encuesta "{question_text}" eliminada exitosamente!')
        return redirect('polls:admin_dashboard')
    
    context = {'question': question}
    return render(request, 'admin/delete_question.html', context)
