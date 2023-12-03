from django.contrib import admin

from .forms import SubCatalogForm
from .models import (
    AdvUser, SubCatalog,
    Lesson, AdditionalImage,
)


admin.site.register(AdvUser)


class SubCatalogInLine(admin.TabularInline):
    model = SubCatalog


class SubCatalogAdmin(admin.ModelAdmin):
    form = SubCatalogForm
    list_display = ('author', 'name',)

admin.site.register(SubCatalog, SubCatalogAdmin)


class AdditionalImageInLine(admin.TabularInline):
    model = AdditionalImage


class LessonAdmin(admin.ModelAdmin):
    list_display = ('catalog', 'title', 'description', 'author', 'date')
    fields = (('catalog', 'author'), 'title', 'description', 'date', 'image')
    inlines = (AdditionalImageInLine,)

admin.site.register(Lesson, LessonAdmin)