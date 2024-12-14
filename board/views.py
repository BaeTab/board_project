from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment, Like
from django.contrib.auth.models import User
from .forms import PostForm, CommentForm
from django.db.models import Count
import random
import requests
from datetime import timedelta
from django.utils import timezone

def get_random_quote():
    quotes = [
        {"text": "삶이 있는 한 희망은 있다.", "author": "키케로"},
        {"text": "산다는 것, 그것은 치열한 전투이다.", "author": "로망로랑"},
        {"text": "하루에 3시간을 걸으면 7년 후에 지구를 한바퀴 돌 수 있다.", "author": "사무엘존슨"},
        {"text": "언제나 현재에 집중할 수 있다면 행복할 것이다.", "author": "파울로 코엘료"},
        {"text": "진정으로 웃으려면 고통을 참아야 하며, 나아가 고통을 즐길 줄 알아야 한다.", "author": "찰리 채플린"},
    ]
    return random.choice(quotes)

@login_required
def post_list(request):
    # 기본 게시글 목록 (최신순)
    posts = Post.objects.all().order_by('-created_at')
    
    # 인기 게시글 (좋아요 많은 순)
    popular_posts = Post.objects.annotate(
        like_count=Count('likes')
    ).order_by('-like_count')[:5]
    
    # 최근 24시간 내 가장 활발한 게시글 (댓글 많은 순)
    recent_active = Post.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=1)
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-comment_count')[:5]
    
    # 오늘의 명언
    quote = get_random_quote()
    
    # 날씨 정보 가져오기 (서귀포시 기준)
    weather_data = None
    try:
        weather_api_key = "13505764fceb0a3c50a7516c046ff0ac"
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q=jejudo&appid={weather_api_key}&units=metric&lang=kr"
        response = requests.get(weather_url)
        if response.status_code == 200:
            weather_data = response.json()
    except:
        weather_data = None
    
    context = {
        'posts': posts,
        'popular_posts': popular_posts,
        'recent_active': recent_active,
        'quote': quote,
        'weather': weather_data,
    }
    return render(request, 'board/post_list.html', context)

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all().order_by('-created_at')
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=pk)
    else:
        form = CommentForm()
    return render(request, 'board/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })

@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'board/post_edit.html', {'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, "You don't have permission to edit this post.")
        return redirect('post_detail', pk=pk)
    
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'board/post_edit.html', {'form': form})

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, "You don't have permission to delete this post.")
        return redirect('post_detail', pk=pk)
    post.delete()
    return redirect('post_list')

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    return redirect('post_detail', pk=pk)

@login_required
def dashboard(request):
    user = request.user
    # 사용자의 최근 게시글
    user_posts = Post.objects.filter(author=user).order_by('-created_at')[:5]
    # 받은 좋아요 수
    total_likes = Like.objects.filter(post__author=user).count()
    # 작성한 댓글 수
    user_comments = Comment.objects.filter(author=user).count()
    # 전체 통계
    total_posts = Post.objects.count()
    total_comments = Comment.objects.count()
    
    context = {
        'user_posts': user_posts,
        'total_likes': total_likes,
        'user_comments': user_comments,
        'total_posts': total_posts,
        'total_comments': total_comments,
    }
    return render(request, 'board/dashboard.html', context)
