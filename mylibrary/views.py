from collections import Counter
import datetime
from functools import reduce
from typing import Any
from django import http
from django.db import models
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic import ListView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import BookCreateForm, CustomUserCreationForm, NextReadsForm, ReadingGoalsForm, AdvancedSearchForm
from .models import Book, NextReads, ReadingGoals, CustomUser

# Create your views here.
# Login view
class LoginRequest(LoginView):
    next_page = 'home'
    template_name='registration/login.html'
    # Logged users are not allowed to access login screen
    @method_decorator(user_passes_test(lambda user: not user.is_authenticated, login_url='home'))
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(request, *args, **kwargs)
    
# User SignUp view
class SignUp(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

# Change Password view
class PasswordChange(LoginRequiredMixin, PasswordChangeView):
    template_name = 'mylibrary/password_change.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Password changed!")
        return super().form_valid(form)

# Home creation
@login_required
def home(request):
    # If user completes the goal, a congratulations message will appear
    if request.method == 'POST':
        goal_id = request.POST.get("goal")
        achieved_goal = ReadingGoals.objects.get(id=goal_id)
        achieved_goal.delete()
        messages.add_message(request, messages.SUCCESS, 'Congratulations!')
        return redirect('/home')

    # collection general inforation
    context = {}
    book_instance = Book.objects.filter(book_owner=request.user)
    nextreads_instance = NextReads.objects.filter(book_owner=request.user)
    readinggoals_instace = ReadingGoals.objects.filter(book_owner=request.user)
    if len(book_instance) == 1:
        context['totalbooks'] = 1
        context['author'] = book_instance[0].author
        context['totalpages'] = book_instance[0].page_numbers
        context['genre'] = book_instance[0].genre
        context['company'] = book_instance[0].publishing_company
    if len(book_instance) > 1:
        context['totalbooks'] = len(book_instance)
        total_pages = 0
        authors_list = []
        genre_list = []
        company_list = []
        for book in book_instance:
            total_pages += book.page_numbers
            authors_list.append(book.author)
            genre_list.append(book.genre)
            company_list.append(book.publishing_company)
        authors, genres, companies = Counter(authors_list), Counter(genre_list), Counter(company_list)
        favorite_author = reduce(lambda author1, author2: author1 if authors[author1] > authors[author2] else author2, authors)
        favorite_genre = reduce(lambda genre1, genre2: genre1 if genres[genre1] > genres[genre2] else genre2, genres)
        favorite_company = reduce(lambda company1, company2: company1 if companies[company1] > companies[company2] else company2, filter(lambda company: company is not None,companies))
        context['author'] = favorite_author
        context['totalpages'] = total_pages
        context['genre'] = favorite_genre
        context['company'] = favorite_company

    if nextreads_instance:
        context['nextread'] = nextreads_instance[0]

    if readinggoals_instace:
        context['readinggoals'] = readinggoals_instace[0]

    # Handling dates
    if readinggoals_instace:
        prazo_maximo = datetime.datetime.strptime(str(readinggoals_instace[0].deadline), '%Y-%m-%d').date()
        time_remaining = str(prazo_maximo - datetime.date.today())
        time_remaining = time_remaining.split(',')
        time_remaining = time_remaining[0].split(' ')
        if str(prazo_maximo - datetime.date.today()) == '0:00:00':
               context['time_remaining'] = 'The deadline is today!'
        elif int(time_remaining[0]) >= 0:
            context['time_remaining'] = f"{time_remaining[0]} days remaining to finish the goal!"
        else:
            context['time_remaining'] = f"Missed the deadline!"
    
    return render(request, 'mylibrary/home.html', context)

# Logout view
def logout_request(request):
    logout(request)
    return redirect('login')

# Profile view
@login_required
def profile(request):
    context = {}
    return render(request, 'mylibrary/profile.html', context)

# Delete User view
class DeleteUser(LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'mylibrary/deleteaccount.html'
    success_url = '/home'

    # If user tries to access another user id, he will be redirected to profile page
    def get_object(self, queryset=None):
        active_user = super().get_object(queryset)
        if self.request.user != active_user:
            return None
        return active_user

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object:
            return redirect('profile')
        return super().get(request, *args, **kwargs)


# Book create view
class BookCreate(LoginRequiredMixin, CreateView):
    model = Book
    template_name = 'mylibrary/book_create.html'
    form_class = BookCreateForm

    # If user selects the 'finished' option in home page, he will be redirected to create book with finished book title as initial value in title field
    def get(self, request, *args, **kwargs):
        if self.request.GET.get('title'):
            nextread_instance = NextReads.objects.get(title=self.request.GET.get('title'))
            if nextread_instance:
                nextread_instance.delete()
        return super().get(request, *args, **kwargs)
    
    def get_initial(self):
        initial = super().get_initial()
        initial['title'] = self.request.GET.get('title')
        return initial

    def form_valid(self, form):
        form.instance.book_owner = self.request.user
        messages.add_message(self.request, messages.SUCCESS, 'Book created!')
        return super().form_valid(form)

# Book list view
class BookList(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'mylibrary/book_list.html'

    def get_queryset(self):
        instances = Book.objects.filter(book_owner=self.request.user)
        return instances

# Book update view
class BookUpdate(LoginRequiredMixin, UpdateView):
    model = Book
    template_name = 'mylibrary/book_update.html'
    form_class = BookCreateForm

    # If user tries to access other users' books, he will be redirected to booklist page
    def get_object(self, queryset=None):
        book = super().get_object(queryset)
        if self.request.user != book.book_owner:
            return None
        return book

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object:
            return redirect('booklist')
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Book updated!')
        return super().form_valid(form)

# Book delete view
class BookDelete(LoginRequiredMixin, DeleteView):
    model = Book
    template_name = 'mylibrary/book_delete.html'
    success_url = '/home'

    # If user tries to access other users' books, he will be redirected to booklist page
    def get_object(self, queryset=None):
        book = super().get_object(queryset)
        if self.request.user != book.book_owner:
            return None
        return book

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object:
            return redirect('booklist')
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Book deleted!')
        return super().form_valid(form)

# Next reads view
class NextReadsCreate(LoginRequiredMixin, CreateView):
    model = NextReads
    template_name = 'mylibrary/next_reads.html'
    form_class = NextReadsForm

    def form_valid(self, form):
        form.instance.book_owner = self.request.user
        messages.add_message(self.request, messages.SUCCESS, 'Next read created!')
        return super().form_valid(form)

# Next reads view
class NextReadsList(LoginRequiredMixin, ListView):
    model = NextReads
    template_name = 'mylibrary/list_next_reads.html'

    def get_queryset(self):
        instances = NextReads.objects.filter(book_owner=self.request.user)
        return instances

# If user tries to access other users' next reads, he will be redirected to next reads page
class NextReadsDelete(LoginRequiredMixin, DeleteView):
    model = NextReads
    template_name = 'mylibrary/next_reads_delete.html'
    success_url = '/home'

    def get_object(self, queryset=None):
        book = super().get_object(queryset)
        if self.request.user != book.book_owner:
            return None
        return book

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object:
            return redirect('/next_reads/list')
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Next read deleted!')
        return super().form_valid(form)

# Goals create view
class ReadingGoalsCreate(LoginRequiredMixin, CreateView):
    model = ReadingGoals
    form_class = ReadingGoalsForm
    template_name = 'mylibrary/goals_create.html'

    def form_valid(self, form):
        form.instance.book_owner = self.request.user
        messages.add_message(self.request, messages.SUCCESS, 'Goal created!')
        return super().form_valid(form)
    
# Goals list view
class ReadingGoalsList(LoginRequiredMixin, ListView):
    model = ReadingGoals
    template_name = 'mylibrary/goals_list.html'

    def get_queryset(self):
        instances = ReadingGoals.objects.filter(book_owner=self.request.user)
        return instances

# Goals delete view
class ReadingGoalsDelete(LoginRequiredMixin, DeleteView):
    model = ReadingGoals
    template_name = 'mylibrary/goals_delete.html'
    success_url = '/home'

    # If user tries to access other users' books, he will be redirected to booklist page
    def get_object(self, queryset=None):
        book = super().get_object(queryset)
        if self.request.user != book.book_owner:
            return None
        return book

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object:
            return redirect('/goals/list')
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Goal deleted!')
        return super().form_valid(form)

# Advanced search view
class AdvancedSearch(LoginRequiredMixin, FormView):
    template_name = 'mylibrary/advanced_search.html'
    form_class = AdvancedSearchForm

    def get(self, request: HttpRequest, *args: str, **kwargs: Any):
        self.context = ''
        self.finish_date = ''
        self.search_type = ''
        search_type = request.GET.get("search_type")
        if search_type == 'title':
            self.context = request.GET.get("title_search")
            self.search_type = 'title'
        elif search_type == 'author':
            self.context = request.GET.get("author_search")
            self.search_type = 'author'
        elif search_type == 'genre':
            self.context = request.GET.get("genre_search")
            self.search_type = 'genre'
        elif search_type == 'publication_year':
            self.context = request.GET.get("publication_year_search")
            self.search_type = 'publication_year'
        elif search_type == 'grade':
            self.context = request.GET.get("grade_search")
            self.search_type = 'grade'
        elif search_type == 'finish_date':
            self.context = request.GET.get("finish_date_search")
            self.finish_date = request.GET.get("finish_date_search2")
            self.search_type = 'finish_date'
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        if self.search_type == 'title':
            context['contexto'] = Book.objects.filter(title__icontains = self.context, book_owner=self.request.user)
        elif self.search_type == 'author':
            context['contexto'] = Book.objects.filter(author__icontains = self.context, book_owner=self.request.user)
        elif self.search_type == 'genre':
            context['contexto'] = Book.objects.filter(genre__icontains = self.context, book_owner=self.request.user)
        elif self.search_type == 'publication_year':
            context['contexto'] = Book.objects.filter(publication_year__icontains = self.context, book_owner=self.request.user)
        elif self.search_type == 'grade':
            context['contexto'] = Book.objects.filter(grade__icontains = self.context, book_owner=self.request.user)
        elif self.search_type == 'finish_date':
            context['contexto'] = Book.objects.filter(finish_read_date__range=(self.context, self.finish_date), book_owner=self.request.user)
        
        return context
