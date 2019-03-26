from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('github_complete/', views.github_complete, name='github_complete'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('update_data/', views.update_data, name='update_data'),
    path('remove_github/', views.remove_github, name='remove_github'),
    path('about/', views.about, name="about")
]
