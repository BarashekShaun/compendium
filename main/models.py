from django.db import models
from django.contrib.auth.models import AbstractUser, User

from main.utilities import get_timestamp_path


class AdvUser(AbstractUser):
    email = models.EmailField('email.', unique=True)
    send_messages = models.BooleanField(default=True,
                                        verbose_name='Получать уведомления о новых записях?')

    def delete(self, *args, **kwargs):
        for catalogs in self.catalog_set.all():
            catalogs.delete()
        super().delete(*args, **kwargs)

    class Meta(AbstractUser.Meta):
        pass


class Catalog(models.Model):
    name = models.CharField(max_length=40, unique=True, verbose_name='Название')
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Порядок')


class SubCatalog(Catalog):
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE,
                               verbose_name='Автор')

    def __str__(self):
        return '%s' % (self.name)

    def delete(self, *args, **kwargs):
        for lesson in self.lesson_set.all():
            lesson.delete()
        super().delete(*args, **kwargs)

    class Meta:

        ordering = ('order',
                    'name')
        verbose_name = 'Подкаталог'


class Lesson(models.Model):
    catalog = models.ForeignKey(SubCatalog, on_delete=models.CASCADE,
                                verbose_name='Курс')
    title = models.CharField(max_length=30, verbose_name='Занятие')
    description = models.TextField(verbose_name='Описание')
    date = models.DateField(verbose_name='Дата занятия', db_index=True)
    image = models.ImageField(blank=True, upload_to=get_timestamp_path,
                              verbose_name='Изображение')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE,
                               verbose_name='Автор')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Добавлено')

    # переопределенный метод delete() перебирает и удаляет все связанные изображения
    def delete(self, *args, **kwargs):
        for image in self.additionalimage_set.all():
            image.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Занятие'
        verbose_name_plural = 'Занятия'
        ordering = ['-created_at']


class AdditionalImage(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE,
                               verbose_name='Занятие')
    image = models.ImageField(upload_to=get_timestamp_path,
                              verbose_name='Изображение')
    class Meta:
        verbose_name = 'Вложенное изображение'






