from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from blog.models import Post, Page
# from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import Http404, HttpRequest, HttpResponse
from django.views.generic import ListView

PER_PAGE = 9


class PostListView(ListView):
    model = Post
    template_name = 'blog/pages/index.html'
    context_object_name = 'posts'
    ordering = '-pk',
    paginate_by = PER_PAGE
    queryset = Post.objects.get_published()  # type:ignore

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     queryset = queryset.filter(is_published=True)
    #     return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'page_title': 'Home - '})
        return context


# def index(request):
#     posts = Post.objects.get_published()  # type:ignore

#     paginator = Paginator(posts, PER_PAGE)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     return render(request, 'blog/pages/index.html', {'page_obj': page_obj, 'page_title': 'Home - ', })


class CreatedByListView(PostListView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._temp_context = {}

    def get(self, request, *args, **kwargs):
        author_pk = self.kwargs.get('author_pk')
        user = User.objects.filter(pk=author_pk).first()

        if user is None:
            raise Http404()

        self._temp_context.update({'author_pk': author_pk, 'user': user, })

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self._temp_context['user']
        user_full_name = user.username

        if user.first_name:
            user_full_name = f'{user.first_name} {user.last_name}'
        page_title = 'Posts de ' + user_full_name + ' - '

        context.update({'page_title': page_title, })

        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(created_by__pk=self._temp_context['user'].pk)
        return queryset


# def created_by(request, author_pk):
#     user = User.objects.filter(pk=author_pk).first()

#     if user is None:
#         raise Http404()

#     posts = Post.objects.get_published().filter(created_by__pk=author_pk)  # type:ignore
#     user_full_name = user.username

#     if user.first_name:
#         user_full_name = f'{user.first_name} {user.last_name}'
#     page_title = 'Posts de ' + user_full_name + ' - '

#     paginator = Paginator(posts, PER_PAGE)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     return render(request, 'blog/pages/index.html', {'page_obj': page_obj, 'page_title': page_title, })


class CategoryListView(PostListView):
    allow_empty = False

    def get_queryset(self):
        return super().get_queryset().filter(category__slug=self.kwargs.get('slug'))

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        page_title = f'Categoria {self.object_list[0].category.name} - '  # type: ignore
        context.update({'page_title': page_title})
        return context


# def category(request, slug):
#     posts = Post.objects.get_published().filter(category__slug=slug)  # type:ignore

#     paginator = Paginator(posts, PER_PAGE)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     if len(page_obj) == 0:
#         raise Http404

#     page_title = f'Categoria {page_obj[0].category.name} - '

#     return render(request, 'blog/pages/index.html', {'page_obj': page_obj, 'page_title': page_title, })


class TagListView(PostListView):
    allow_empty = False

    def get_queryset(self):
        return super().get_queryset().filter(tags__slug=self.kwargs.get('slug'))

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        page_title = f'Tag {self.object_list[0].tags.filter(slug=slug).first().name} - '  # type: ignore
        context.update({'page_title': page_title})
        return context


# def tag(request, slug):
#     posts = Post.objects.get_published().filter(tags__slug=slug)  # type:ignore

#     paginator = Paginator(posts, PER_PAGE)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     if len(page_obj) == 0:
#         raise Http404

#     page_title = f'Tag {page_obj[0].tags.filter(slug=slug).first().name} - '

#     return render(request, 'blog/pages/index.html', {'page_obj': page_obj, 'page_title': page_title, })


class SearchListView(PostListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._search_value = ''

    def setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        self._search_value = request.GET.get('search', '').strip()
        return super().setup(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if self._search_value == '':
            return redirect('blog:index')
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Any]:
        search_value = self._search_value
        return super().get_queryset().filter(
            Q(title__icontains=search_value) |
            Q(excerpt__icontains=search_value) |
            Q(content__icontains=search_value)
        )[:PER_PAGE]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_value = self._search_value
        context.update({
            'page_title': f'Busca {search_value[:30]} - ',
            'search_value': search_value,
        })
        return context


# def search(request):
#     search_value = request.GET.get('search', '').strip()
#     posts = (
#         Post.objects.get_published()  # type:ignore
#         .filter(
#             Q(title__icontains=search_value) |
#             Q(excerpt__icontains=search_value) |
#             Q(content__icontains=search_value)
#         )[:PER_PAGE]
#     )

#     page_title = f'Busca {search_value[:30]} - '

#     # paginator = Paginator(posts, PER_PAGE)
#     # page_number = request.GET.get('page')
#     # page_obj = paginator.get_page(page_number)

#     return render(request, 'blog/pages/index.html', {'page_obj': posts,
#                                                      'search_value': search_value,
#                                                      'page_title': page_title, })


def page(request, slug):
    page_obj = Page.objects.filter(is_published=True).filter(slug=slug).first()

    if page_obj is None:
        raise Http404

    page_title = f'{page_obj.title} - '

    return render(request, 'blog/pages/page.html', {'page': page_obj, 'page_title': page_title, })


def post(request, slug):
    post_obj = Post.objects.get_published().filter(slug=slug).first()  # type:ignore

    if post_obj is None:
        raise Http404

    page_title = f'{post_obj.title} - '

    return render(request, 'blog/pages/posts.html', {'post': post_obj, 'page_title': page_title, })
