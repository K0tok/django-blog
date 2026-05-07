from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from .models import Post, Comment, Category
from .forms import CommentForm, RegisterForm


def register(request):
    """Страница регистрации пользователя"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            # Автоматическая авторизация после регистрации
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('post_list')
    else:
        form = RegisterForm()
    
    context = {
        'form': form,
    }
    return render(request, 'blog/register.html', context)


def post_list(request):
    """Главная страница со списком всех статей"""
    category_slug = request.GET.get('category')
    search_query = request.GET.get('search', '')
    
    posts = Post.objects.all()
    categories = Category.objects.all()
    
    # Фильтрация по категории
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    # Поиск по статьям
    if search_query:
        posts = posts.filter(title__icontains=search_query) | posts.filter(content__icontains=search_query)
    
    # Пагинация
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query,
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    """Страница с деталями статьи"""
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.all()
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', slug=post.slug)
    else:
        form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'blog/post_detail.html', context)
