
from django.urls import path

from . import views

app_name = "network"

urlpatterns = [
    path("", views.index, name="index"),
    path('profile/<str:username>/', views.profile, name='profile'),  # Ruta para ver el perfil de usuario
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('follow/<str:username>/', views.follow, name='follow'),
    path('unfollow/<str:username>/', views.unfollow, name='unfollow'),
    path('following/', views.following, name='following'),
    path('save_post/<int:post_id>/', views.save_post, name='save_post'),
    path('toggle_like/<int:post_id>/', views.toggle_like, name='toggle_like'),

]
