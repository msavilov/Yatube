from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post
from .paginators import paginator

CACHE_TIME = 20

User = get_user_model()


@cache_page(CACHE_TIME, key_prefix='index_page')
def index(request):
    post_list = Post.objects.select_related(
        'author', 'group')
    page_obj = paginator(post_list, request)
    context = {
        'title': 'Это главная страница проекта Yatube',
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


@cache_page(CACHE_TIME)
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author')
    page_obj = paginator(post_list, request)
    context = {
        'group': group,
        'page_obj': page_obj,
        'title': group.title
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.select_related('author', 'group').filter(
        author__username=username)
    page_obj = paginator(post_list, request)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author).exists()
    else:
        following = False
    context = {
        'author': author,
        'count': post_list.count(),
        'following': following,
        'page_obj': page_obj,
        'title': f'Профайл пользователя {author}',
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'), id=post_id)
    form = CommentForm()
    comments = Comment.objects.select_related('author').filter(post=post_id)
    context = {
        'author': post.author,
        'comments': comments,
        'form': form,
        'post': post,
        'preview': str(post),
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if not form.is_valid():
        return render(request, 'posts/edit_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', post.author)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/edit_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'includes/comments.html', {'form': form,
                  'post': post})


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(post_list, request)
    context = {
        'page_obj': page_obj,
        'title': 'Страница с подписками',
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    is_follower = Follow.objects.filter(user=user, author=author)
    if user != author and not is_follower.exists():
        Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=request.user, author=author)
    if is_follower.exists():
        is_follower.delete()
    return redirect('posts:profile', username=author)
