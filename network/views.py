from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Count


from .models import User, Post, Follow, Like


def index(request):
    if request.method == "POST":
        content = request.POST["content"]  # Asegúrate de que el nombre del campo coincide
        user = request.user
        new_post = Post(user=user, content=content)
        new_post.save()
        return HttpResponseRedirect(reverse("network:index"))  # Usa el namespace correcto
    else:
        posts = Post.objects.all().annotate(likes_count=Count('liked')).order_by('-timestamp')  # Ordenar por timestamp en orden descendente
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
    user = User.objects.get(username=username)
    
    # Obtener los conteos de seguidores y seguidos utilizando los nombres correctos de los campos relacionados
    user_with_counts = User.objects.filter(username=username).annotate(
        followers_count=Count('followed'),  # followed es el related_name para los seguidores
        following_count=Count('follower')   # follower es el related_name para los seguidos
    ).get()
    
    posts = Post.objects.filter(user=user).annotate(likes_count=Count('liked')).order_by('-timestamp')

    return render(request, "network/profile.html", {
        "posts": posts,
        "user": user,
        "followers_count": user_with_counts.followers_count,
        "following_count": user_with_counts.following_count
    })


def follow(request, username):
    user = request.user
    following = User.objects.get(username=username)
    new_follow = Follow(user=user, following=following)
    new_follow.save()
    return HttpResponseRedirect(reverse("network:profile", args=(username,)))


def unfollow(request, username):
    user = request.user
    following = User.objects.get(username=username)
    Follow.objects.filter(user=user, following=following).delete()
    return HttpResponseRedirect(reverse("network:profile", args=(username,)))



