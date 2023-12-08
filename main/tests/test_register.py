from django.contrib.auth import get_user_model
from django.test import TestCase


class AdvUserRegisterTest(TestCase):
    def setUp(self):
        self.username = 'tomato'
        self.password1 = 'tomat235O'
        self.password2 = 'tomat235O'
        self.email = 't@tomato.com'

    def test_register_url(self):
        response = self.client.get('/accounts/register/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='main/register.html')

    def test_register_user(self):
        response = self.client.post('/accounts/register/', data= {
            'username': self.username,
            'email': self.email,
            'password1': self.password1,
            'password2': self.password2,
        })
        self.assertEqual(response.status_code, 302)

        new_user = get_user_model().objects.get(
            username=self.username
        )
        self.assertEqual(self.email, new_user.email)


    def test_failed_register(self):
        response = self.client.post('/accounts/register/', data={
            'username': self.username,
            'email': self.email,
            'password1': self.password1,
            'password2': 'tt',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response,
            'form',
            'password2',
            'Пароли не совпадают'
        )