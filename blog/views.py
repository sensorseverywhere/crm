from django.shortcuts import redirect, render
from .forms import BlogForm
from .models import Blog


def post_detail(request, pk):
    post = Blog.objects.get(id=pk)
    context = {
        'post': post
    }
    return render(request, 'posts/post_detail.html', context)


def post_list(request):
    posts = Blog.objects.all()
    context = {
        'posts': posts
    }
    return render(request, 'posts/post_list.html', context)


def post_update(request, pk):
    blogpost = Blog.objects.get(id=pk)
    form = BlogForm()
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            post = form.cleaned_data['post']
            blogpost.title = title
            blogpost.post = post
            blogpost.save()
            return redirect('posts/')
    context = {
        'form': form
    }
    return render(request, 'posts/post_update.html', context)


def post_create(request):
    form = BlogForm()
    if request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            post = form.cleaned_data['post']
            new_post = Blog.objects.create(
                title=title,
                post=post,
            )
            new_post.save()
            return redirect('/posts')
    context = {
        'form': form
    }
    return render(request, 'posts/post_create.html', context)