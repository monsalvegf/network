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
    posts = Post.objects.filter(user=user).annotate(likes_count=Count('liked'))

    return render(request, "network/profile.html", {
        "posts": posts,
        "user": user
    })



