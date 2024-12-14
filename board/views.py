from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment, Like
from django.contrib.auth.models import User
from .forms import PostForm, CommentForm

@login_required
def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'board/post_list.html', {'posts': posts})

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
