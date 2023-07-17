from django.urls import path
from . import views

urlpatterns = [
    path('', views.LoginRequest.as_view(), name='login'),
    path('home/', views.home, name='home'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('logout/', views.logout_request, name='logout'),
    path('book/create', views.BookCreate.as_view(), name='bookcreate'),
    path('book/list', views.BookList.as_view(), name='booklist'),
    path('book/<pk>/update', views.BookUpdate.as_view(), name='bookupdate'),
    path('book/<pk>/delete', views.BookDelete.as_view(), name='bookdelete'),
    path('profile/password_change/', views.PasswordChange.as_view(), name='passwordchange'),
    path('next_reads/create', views.NextReadsCreate.as_view(), name='nextreadscreate'),
    path('next_reads/list', views.NextReadsList.as_view(), name='nextreadslist'),
    path('next_reads/<pk>/delete', views.NextReadsDelete.as_view(), name='nextreadsdelete'),
    path('goals/new/', views.ReadingGoalsCreate.as_view(), name='goalscreate'),
    path('goals/list/', views.ReadingGoalsList.as_view(), name='goalslist'),
    path('goals/<pk>/delete', views.ReadingGoalsDelete.as_view(), name='goalsdelete'),
    path('advanced_search/', views.AdvancedSearch.as_view(), name='advancedsearch'),
    path('profile/', views.profile, name='profile'),
    path('account/<pk>/delete/', views.DeleteUser.as_view(), name='deleteaccount')
]