from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from django.db.models import Count
from .models import Post, Comment, Like, UserProfile
from .forms import PostForm, CommentForm, CustomUserCreationForm
import random
import requests
from datetime import timedelta

def get_random_quote():
    quotes = [
        # 한국 명언
        {"text": "삶이 있는 한 희망은 있다.", "author": "키케로"},
        {"text": "산다는 것, 그것은 치열한 전투이다.", "author": "로망로랑"},
        {"text": "하루에 3시간을 걸으면 7년 후에 지구를 한바퀴 돌 수 있다.", "author": "사무엘존슨"},
        {"text": "언제나 현재에 집중할 수 있다면 행복할 것이다.", "author": "파울로 코엘료"},
        {"text": "진정으로 웃으려면 고통을 참아야 하며, 나아가 고통을 즐길 줄 알아야 한다.", "author": "찰리 채플린"},
        
        # 한국 철학자와 작가들의 명언
        {"text": "나는 아직 나의 길을 가고 있다.", "author": "윤동주"},
        {"text": "인생에서 가장 중요한 것은 살아가는 자세다.", "author": "정약용"},
        {"text": "실패는 성공의 어머니다.", "author": "김구"},
        {"text": "꿈을 이루고자 하는 용기만 있다면 모든 꿈은 이루어질 수 있다.", "author": "박지성"},
        {"text": "오늘 할 수 있는 일을 내일로 미루지 마라.", "author": "정철"},
        
        # 세계적인 명언들
        {"text": "나는 생각한다. 고로 존재한다.", "author": "데카르트"},
        {"text": "지식은 힘이다.", "author": "프랜시스 베이컨"},
        {"text": "성공은 실패를 두려워하지 않는 자의 것이다.", "author": "월트 디즈니"},
        {"text": "변화는 우리가 세상을 보는 방식이다.", "author": "알버트 아인슈타인"},
        {"text": "작은 것을 소중히 여기는 자에게 큰 것도 따라온다.", "author": "공자"},
        
        # 현대적이고 동기부여하는 명언들
        {"text": "불가능이란 단지 당신의 제한된 믿음일 뿐이다.", "author": "웨인 다이어"},
        {"text": "당신의 태도가 당신의 방향을 결정한다.", "author": "짐 론"},
        {"text": "성공은 하루아침에 이루어지지 않는다.", "author": "헨리 포드"},
        {"text": "두려움을 극복하는 유일한 방법은 두려움과 맞서는 것이다.", "author": "브라이언 트레이시"},
        {"text": "당신의 열정이 당신의 길을 비춘다.", "author": "스티브 잡스"},
        
        # 코딩 및 개발 관련 명언들
        {"text": "좋은 코드는 좋은 문서만큼 중요하다.", "author": "로버트 마틴"},
        {"text": "완벽한 코드는 없다. 다만 더 나은 코드만 있을 뿐이다.", "author": "켄트 벡"},
        {"text": "코드를 작성할 때는 그 코드를 읽을 다른 개발자를 존중하는 마음으로 작성하라.", "author": "로버트 C. 마틴"},
        {"text": "디버깅은 코드를 작성하는 것보다 두 배는 어렵다. 그러므로 가능한 한 똑똑하게 코드를 작성하라.", "author": "브라이언 커니핸"},
        {"text": "소프트웨어 개발에서 가장 중요한 것은 복잡성을 줄이는 것이다.", "author": "에릭 레이먼드"},
        {"text": "코드는 읽기 쉬워야 한다. 컴퓨터가 이해할 수 있는 코드는 바보도 작성할 수 있다.", "author": "마틴 파울러"},
        {"text": "좋은 프로그래머는 코드를 작성하고, 훌륭한 프로그래머는 코드를 재사용한다.", "author": "톰 프레스턴-워너"},
        {"text": "실패는 배움의 기회일 뿐이다. 포기하지 마라.", "author": "팀 버너스리"},
        {"text": "기술은 계속 변화한다. 중요한 건 학습하는 능력이다.", "author": "스티브 잡스"},
        {"text": "코드는 시간이 지날수록 더 나은 개발자가 되는 거울이다.", "author": "앤디 헌트"}
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
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q=jejucity&appid={weather_api_key}&units=metric&lang=kr"
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

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            messages.success(request, '회원가입이 완료되었습니다. 관리자의 승인을 기다려주세요.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def pending_users(request):
    pending_profiles = UserProfile.objects.filter(is_approved=False, user__is_active=False)
    return render(request, 'board/pending_users.html', {'pending_profiles': pending_profiles})

@user_passes_test(lambda u: u.is_superuser)
def approve_user(request, user_id):
    user_profile = get_object_or_404(UserProfile, user_id=user_id)
    user = user_profile.user
    user.is_active = True
    user.save()
    user_profile.is_approved = True
    user_profile.save()
    messages.success(request, f'사용자 {user.username}이(가) 승인되었습니다.')
    return redirect('pending_users')
