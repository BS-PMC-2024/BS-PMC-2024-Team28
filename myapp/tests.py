from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import UserProfileForm
from django.contrib.auth.models import User

class UserProfileUpdateTests(TestCase):

    def setUp(self):
        # Create a user and profile
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user_profile = UserProfile.objects.create(user=self.user, bio='Initial bio')

        # Log in the user
        self.client.login(username='testuser', password='testpassword')

    def test_update_profile_get(self):
        response = self.client.get(reverse('update_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_profile.html')
        self.assertContains(response, '<form')

    def test_update_profile_post_valid(self):
        response = self.client.post(reverse('update_profile'), {
            'bio': 'Updated bio',
            'profile_picture': None  # Assuming no file upload for simplicity
        })
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.user_profile.refresh_from_db()
        self.assertEqual(self.user_profile.bio, 'Updated bio')

    def test_update_profile_post_invalid(self):
        response = self.client.post(reverse('update_profile'), {
            'bio': '',  # Invalid data
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'bio', 'This field is required.')

    def test_profile_update_redirect_for_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(reverse('update_profile'))
        self.assertRedirects(response, '/IDAS_3/loginuser/?next=/profile/update/')





class LoginTests(TestCase):

    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_login_page_loads(self):
        response = self.client.get(reverse('loginuser'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'loginuser.html')

    def test_login_valid_user(self):
        response = self.client.post(reverse('loginuser'), {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertRedirects(response, reverse('chatPage'))  # Check redirection to chatPage

    def test_login_invalid_user(self):
        response = self.client.post(reverse('loginuser'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password.')

    def test_login_redirect_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(reverse('loginuser'))
        self.assertRedirects(response, '/IDAS_3/loginuser/?next=/loginuser/')


class SignupTests(TestCase):

    def test_signup_page_loads(self):
        response = self.client.get(reverse('signupuser'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signupuser.html')

    def test_signup_valid_user(self):
        response = self.client.post(reverse('signupuser'), {
            'username': 'newuser',
            'password1': 'newpassword',
            'password2': 'newpassword'
        })
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_signup_invalid_user(self):
        response = self.client.post(reverse('signupuser'), {
            'username': 'newuser',
            'password1': 'newpassword',
            'password2': 'differentpassword'  # Passwords don't match
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password2', 'The two password fields must match.')

    def test_signup_redirect_authenticated_user(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('signupuser'))
        self.assertRedirects(response, '/')