from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from apps.core.models import Category, QuizAttempt


def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()

        if not username or not password1:
            messages.error(request, '请把所有信息填写完整～')
        elif password1 != password2:
            messages.error(request, '两次密码不一致，请重新输入。')
        elif len(password1) < 6:
            messages.error(request, '密码至少要 6 位哦。')
        elif User.objects.filter(username=username).exists():
            messages.error(request, '这个用户名已经有人用了，换一个吧。')
        else:
            user = User.objects.create_user(username=username, password=password1)
            login(request, user)
            messages.success(request, f'欢迎加入，{username}！')
            return redirect('index')

    return render(request, 'register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get("next", "")
            if not url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                next_url = "index"
            return redirect(next_url) if next_url else redirect("index")
        else:
            messages.error(request, "用户名或密码不对，再试试看～")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def profile_view(request):
    categories = Category.objects.annotate(
        item_count=Count("items"),
        learned_count=Count(
            "items__progress",
            filter=Q(
                items__progress__user=request.user,
                items__progress__learned=True,
            ),
        ),
    )

    stats = []
    total_learned = 0
    total_items = 0

    for cat in categories:
        item_count = cat.item_count
        learned_count = cat.learned_count
        total_learned += learned_count
        total_items += item_count

        stats.append({
            "category": cat,
            "total": item_count,
            "learned": learned_count,
            "percent": round(learned_count / item_count * 100) if item_count > 0 else 0,
        })

    recent_quizzes = QuizAttempt.objects.filter(
        user=request.user
    ).order_by("-created_at")[:10]

    context = {
        "stats": stats,
        "total_learned": total_learned,
        "total_items": total_items,
        "recent_quizzes": recent_quizzes,
    }
    return render(request, "profile.html", context)
