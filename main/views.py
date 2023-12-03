from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import AdvUser, SubCatalog, Lesson
from .forms import ProfileEditForm, RegisterForm, SearchForm, LessonForm, AIFormSet, SubCatalogForm


def index(request):
    lesson = Lesson.objects.filter(author=request.user.pk).select_related('catalog')[:4]
    context = {'lesson': lesson}
    return render(request, 'main/index.html', context)


"""
Контроллер для автоматического формирования путей вспомогательных страниц
"""
def other_page(request, page):
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


class CustomLoginView(LoginView):
    template_name = 'main/login.html'



class CustomLogoutView(LogoutView):
    pass


class RegisterView(CreateView):
    model = AdvUser
    template_name = 'main/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('main:register_done')


class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'


"""
Декоратор ограничивает видимость профиля для 
незарегистрированных и не вошедших пользователей
"""

@login_required
def catalog(request):
    catalog = SubCatalog.objects.filter(author=request.user.pk)
    context = {'catalog': catalog}
    return render(request, 'main/catalog.html', context)


"""
Суперкласс LoginRequiredMixin запрещает доступ к контроллеру гостям,
SuccessMessageMixin используется для вывода всплывающих сообщений
"""
class ProfileEditView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'main/profile_edit.html'
    form_class = ProfileEditForm
    success_url = reverse_lazy('main:index')
    success_message = 'Данные изменены'

    # Получаем ключ текущего пользователя
    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    # Вытаскиваем пользователя по ключу
    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class PasswordEditView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'main/password_edit.html'
    success_url = reverse_lazy('main:index')
    success_message = 'Пароль успешно изменен'


class ProfileDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'main/profile_delete.html'
    success_message = 'Пользователь удален'
    success_url = reverse_lazy('main:index')

    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)

    # переопределенный метод post выполняет выход
    def post(self, request, *args, **kwargs):
        logout(request)
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


def catalog_lesson(request, pk):
    catalog = get_object_or_404(SubCatalog, pk=pk)
    lesson = Lesson.objects.filter(catalog=pk)

    # фильтрация по введенному слову
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(description__icontains=keyword)
        lesson = lesson.filter(q)
    else:
        keyword = ''
    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(lesson, 5)

    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context = {'catalog': catalog, 'page': page, 'lesson': page.object_list,
               'form': form}

    return render (request, 'main/catalog_lesson.html', context)


@login_required
def profile_catalog_add(request):
    if request.method == 'POST':
        catalog = SubCatalogForm(request.POST)
        if catalog.is_valid():
            catalog.save()
            return redirect('main:catalog')
    else:
        form = SubCatalogForm(initial={'author': request.user.pk})
        context = {'form': form}
    return render(request, 'main/catalog_add.html', context)


def lesson_detail(request, catalog_pk, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    adill = lesson.additionalimage_set.all()
    context = {'lesson': lesson, 'adill': adill}
    return render(request, 'main/lesson_detail.html', context)


"""
Сохранение формы происходит заранее для того, чтобы все дополнительные иллюстрации оказались связаны с
занятием после их сохранения
"""
@login_required
def profile_lesson_add(request):
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=lesson)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Конспект добавлен')
                return redirect('main:index')
    else:
        form = LessonForm(initial={'author': request.user.pk})
        formset = AIFormSet()
    context = {'form': form, 'formset': formset}

    return render(request, 'main/lesson_add.html', context)


@login_required
def profile_lesson_edit(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            lesson = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=lesson)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Конспект обновлен')
                return redirect('main:index')
    else:
        form = LessonForm(instance=lesson)
        formset = AIFormSet(instance=lesson)
    context = {'form': form, 'formset': formset}
    return render(request, 'main/lesson_edit.html', context)


@login_required
def profile_lesson_delete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST':
        lesson.delete()
        messages.add_message(request, messages.SUCCESS, 'Конспект удален')
        return redirect('main:index')
    else:
        context = {'lesson': lesson}
        return render(request, 'main/lesson_delete.html', context)


@login_required
def profile_catalog_edit(request, pk):
    catalog = get_object_or_404(SubCatalog, pk=pk)
    if request.method == 'POST':
        form = SubCatalogForm(request.POST, instance=catalog)
        form.save()
        messages.add_message(request, messages.SUCCESS, 'Курс обновлен')
        return redirect('main:index')
    else:
        form = SubCatalogForm(instance=catalog)
        context = {'form': form}
        return render(request, 'main/catalog_edit.html', context)

@login_required
def profile_catalog_delete(request, pk):
    catalog = get_object_or_404(SubCatalog, pk=pk)
    if request.method == 'POST':
        catalog.delete()
        messages.add_message(request, messages.SUCCESS, 'Курс удален')
        return redirect('main:index')
    else:
        context = {'catalog': catalog}
        return render(request, 'main/catalog_delete.html', context)

