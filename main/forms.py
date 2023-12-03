from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from .models import AdvUser, SubCatalog, Lesson, AdditionalImage


class RegisterForm(forms.ModelForm):
    email = forms.EmailField(required=True, label='Электронная почта')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput,
                                help_text=password_validation.password_validators_help_text_html())
    password2 = forms.CharField(label='Пароль повторно', widget=forms.PasswordInput,
                                help_text='Пароли должны совпадать')

    # функция выполняет валидацию первого пароля
    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    # функция выполняет проверку совпадения паролей 1 и 2
    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError(
                'Пароли не совпадают', code='password_mismatch'
            )}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'password1', 'password2',
                  'first_name', 'last_name', 'send_messages')


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = AdvUser
        fields = ('username', 'email', 'first_name',
                  'last_name', 'send_messages')


class SubCatalogForm(forms.ModelForm):
    class Meta:
        model = SubCatalog
        fields = ('name', 'author', 'viewers')
        widgets = {'author': forms.HiddenInput}


class SearchForm(forms.Form):
    keyword = forms.CharField(required=False, max_length=30, label='')


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = '__all__'
        widgets = {'author': forms.HiddenInput}

    # переопределяем метод инит, чтобы пользователь видел только свои курсы
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.fields['catalog'].queryset = SubCatalog.objects.filter(author=self.initial['author'])
        except:
            pass




AIFormSet = forms.inlineformset_factory(Lesson, AdditionalImage, fields='__all__')