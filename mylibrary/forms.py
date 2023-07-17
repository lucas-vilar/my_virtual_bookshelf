from dataclasses import fields
from django.contrib.auth import get_user_model
from django import forms
from django.forms import DateInput
from .models import Book, CustomUser, NextReads, ReadingGoals
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

#Custom user form
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2')

#Custom User change form
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')

#Book create form
class BookCreateForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class' : 'createbook-title'}))
    author = forms.CharField(widget=forms.TextInput(attrs={'class' : 'createbook-author'}))
    genre = forms.CharField(widget=forms.TextInput(attrs={'class' : 'createbook-genre'}))
    page_numbers = forms.IntegerField(widget=forms.NumberInput(attrs={'class' : 'createbook-pagenumbers'}))
    publication_year = forms.IntegerField(widget=forms.NumberInput(attrs={'class' : 'createbook-publicationyear'}))
    grade = forms.IntegerField(widget=forms.NumberInput(attrs={'class' : 'createbook-grade'}))
    finish_read_date = forms.DateField(widget=DateInput(attrs={'type':'date', 'class' : 'createbook-date'}))
    publishing_company = forms.CharField(widget=forms.TextInput(attrs={'class' : 'createbook-publisher'}))
    book_cover = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class' : 'createbook-file'}))

    class Meta:
        model = Book
        fields = ('title', 'author', 'genre', 'page_numbers', 'publication_year', 'grade', 'finish_read_date', 'publishing_company', 'review', 'book_cover')

#Next reads form
class NextReadsForm(forms.ModelForm):
    class Meta:
        model = NextReads
        fields = ('title',)

#Reading goals form
class ReadingGoalsForm(forms.ModelForm):
    deadline = forms.DateField(widget=DateInput(attrs={'type':'date'}))
    
    class Meta:
        model = ReadingGoals
        fields = ('goal', 'deadline')

#Advanced search form
class AdvancedSearchForm(forms.Form):
    search_type = forms.ChoiceField(choices=[
        ('title', 'Title'),
        ('author', 'Author'),
        ('genre', 'Genre'),
        ('publication_year', 'Publication year'),
        ('grade', 'Grade'),
        ('finish_date', 'Finish date')
    ], widget=forms.RadioSelect(attrs={"onclick": "showInput()"}))

    title_search = forms.CharField(max_length=150, required=False)
    author_search = forms.CharField(max_length=100, required=False)
    genre_search = forms.CharField(max_length=50, required=False)
    publication_year_search = forms.CharField(max_length=4, required=False)
    grade_search = forms.IntegerField(required=False)
    finish_date_search = forms.DateField(widget=DateInput(attrs={'type':'date'}), required=False)
    finish_date_search2 = forms.DateField(widget=DateInput(attrs={'type':'date'}), required=False)