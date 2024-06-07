from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from .models import User, Post, Follow, Like


def index(request):
    if request.method == "POST":
        content = request.POST["content"]
        user = request.user
        new_post = Post(user=user, content=content)
        new_post.save()
        return HttpResponseRedirect(reverse("network:index"))
    else:
        posts_list = Post.objects.all().annotate(likes_count=Count('liked')).order_by('-timestamp')
        paginator = Paginator(posts_list, 10)  # Mostrar 10 posts por página
        page_number = request.GET.get('page')  # Obtener el número de página desde el URL
        posts = paginator.get_page(page_number)  # Obtener los posts para la página requerida
        return render(request, "network/index.html", {"posts": posts})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("network:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("network:index"))
    else:
        return render(request, "network/register.html")


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    
    # Obtener los conteos de seguidores y seguidos
    user_with_counts = User.objects.filter(username=username).annotate(
        followers_count=Count('followed'),  # followed es el related_name para los seguidores
        following_count=Count('follower')   # follower es el related_name para los seguidos
    ).get()
    
    posts = Post.objects.filter(user=user_profile).annotate(likes_count=Count('liked')).order_by('-timestamp')

    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user, following=user_profile).exists()

    return render(request, "network/profile.html", {
        "posts": posts,
        "user_profile": user_profile,
        "followers_count": user_with_counts.followers_count,
        "following_count": user_with_counts.following_count,
        "following": following
    })

@login_required
def follow(request, username):
    profile_user = get_object_or_404(User, username=username)
    if request.user != profile_user:
        Follow.objects.get_or_create(user=request.user, following=profile_user)
    return redirect('network:profile', username=username)

@login_required
def unfollow(request, username):
    profile_user = get_object_or_404(User, username=username)
    if request.user != profile_user:
        Follow.objects.filter(user=request.user, following=profile_user).delete()
    return redirect('network:profile', username=username)

@login_required
def following(request, username):
    # Obtener el perfil de usuario; asegurándose de que existe.
    user_profile = get_object_or_404(User, username=username)
    
    # Obtener posts asociados al usuario, ordenados por fecha de creación en orden descendente.
    posts = Post.objects.filter(user=user_profile).order_by('-timestamp')
    
    # Renderizar la vista con los posts obtenidos.
    return render(request, "network/following.html", {"posts": posts})

@login_required
def following(request):
    # Obtener el usuario actual.
    user = request.user
    
    # Obtener los usuarios que el usuario actual sigue.
    following_users = User.objects.filter(followed__user=user)
    
    # Obtener posts de los usuarios seguidos, ordenados por fecha de creación en orden descendente, en grupos de 10 por página.
    posts_list = Post.objects.filter(user__in=following_users).order_by('-timestamp')
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # Renderizar la vista con los posts obtenidos.
    return render(request, "network/following.html", {"posts": posts})

@require_POST
@csrf_exempt
def save_post(request, post_id):
    try:
        content = json.loads(request.body).get('content')
        post = Post.objects.get(id=post_id, user=request.user)  # Ensures only the owner can edit
        post.content = content
        post.save()
        return JsonResponse({"message": "Post updated successfully."}, status=200)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found or permission denied."}, status=404)



