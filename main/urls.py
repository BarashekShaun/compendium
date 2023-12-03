from django.urls import path
from .views import (
    index, other_page, CustomLoginView, catalog,
    CustomLogoutView, ProfileEditView, RegisterView,
    RegisterDoneView, PasswordEditView, ProfileDeleteView,
    catalog_lesson, lesson_detail, profile_lesson_add, profile_catalog_add, profile_lesson_edit, profile_lesson_delete,
    profile_catalog_delete, profile_catalog_edit,

)


app_name = 'main'

urlpatterns = [
    path('accounts/password/edit/', PasswordEditView.as_view(), name='password_edit'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('accounts/profile/delete/', ProfileDeleteView.as_view(), name='profile_delete'),
    path('accounts/profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
    path('accounts/catalog/lesson/add', profile_lesson_add, name='lesson_add'),
    path('accounts/catalog/lesson/edit/<int:pk>/', profile_lesson_edit, name='lesson_edit'),
    path('accounts/catalog/lesson/delete/<int:pk>/', profile_lesson_delete, name='lesson_delete'),
    path('accounts/catalog/', catalog, name='catalog'),
    path('accounts/catalog/add', profile_catalog_add, name='catalog_add'),
    path('accounts/catalog/edit/<int:pk>/', profile_catalog_edit, name='catalog_edit'),
    path('accounts/catalog/delete/<int:pk>/', profile_catalog_delete, name='catalog_delete'),
    path('accounts/logout/', CustomLogoutView.as_view(), name='logout'),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('<int:catalog_pk>/<int:pk>/', lesson_detail, name='lesson_detail'),
    path('<int:pk>/', catalog_lesson, name='catalog_lesson'),
    path('<str:page>/', other_page, name='other'),
    path('', index, name='index'),
]