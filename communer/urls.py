from django.urls import path

from communer.views import RegisterUserView, ProjectsListView, TasksListView, TaskCreateView, \
    UserLoginView, ProjectCreatorView, ProjectRetrieveView

urlpatterns = [
    path('register/', RegisterUserView.as_view()),
    path('login/', UserLoginView.as_view()),
    path('projects/create/', ProjectCreatorView.as_view()),
    path('projects/item/<int:pk>/', ProjectRetrieveView.as_view()),
    path('projects/', ProjectsListView.as_view()),
    path('tasks/create/', TaskCreateView.as_view()),
    path('tasks/', TasksListView.as_view()),
]
