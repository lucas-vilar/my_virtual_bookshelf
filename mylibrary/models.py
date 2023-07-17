from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
#Custom User model
class CustomUser(AbstractUser):
    pass

#Book model
class Book(models.Model):
    title = models.CharField(max_length=150, unique=True)
    author = models.CharField(max_length=100)
    genre = models.CharField(max_length=20)
    page_numbers = models.IntegerField(validators=[MinValueValidator(0, 'Please choose a positive number')])
    publication_year = models.IntegerField(blank=True, null=True)
    grade = models.IntegerField(validators= [MinValueValidator(0, 'It is impossible to have a negative grade'), MaxValueValidator(10, 'It is impossible to have a grade greater than 10')])
    finish_read_date = models.DateField(blank=True, null=True)
    publishing_company = models.CharField(max_length=50, blank=True, null=True)
    review = models.TextField(blank=True, null=True)
    book_cover = models.ImageField(upload_to='books/')
    book_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return '/home'

    class Meta:
        db_table = 'book'

#Next reads model
class NextReads(models.Model):
    title = models.CharField(max_length=150, unique=True)
    book_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    def get_absolute_url(self):
        return '/home/'

    class Meta:
        db_table = 'next_reads'

#Goals model
class ReadingGoals(models.Model):
    goal = models.TextField(max_length=500, unique=True)
    deadline = models.DateField()
    book_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return '/home'

    class Meta:
        db_table = 'reading_goals'
        