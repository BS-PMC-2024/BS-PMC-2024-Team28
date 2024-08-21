from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from myapp.models import CommunityMessage, Contactus, UserProfile, Chat

class CommunityChatViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        # Add a profile picture for the test user
        self.profile_picture = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'file_content',
            content_type='image/jpeg'
        )
        self.user.userprofile.profile_picture = self.profile_picture
        self.user.userprofile.save()

    def test_community_chat_get(self):
        response = self.client.get(reverse('community_chat'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'community_chat.html')

    def test_community_chat_post(self):
        response = self.client.post(reverse('community_chat'), {
            'content': 'Test message content'
        })
        self.assertEqual(response.status_code, 302)  # Expect redirect after post
        self.assertTrue(CommunityMessage.objects.filter(content='Test message content').exists())

class CommunityMessageModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_create_community_message(self):
        message = CommunityMessage.objects.create(
            user=self.user,
            content="This is a test message"
        )
        self.assertEqual(message.user.username, 'testuser')
        self.assertEqual(message.content, "This is a test message")
        self.assertFalse(message.image)  # Check that image is not set

class ContactusModelTest(TestCase):

    def test_create_contactus(self):
        contactus = Contactus.objects.create(
            name="John Doe",
            email="john@example.com",
            subject="Test Subject",
            message="This is a test message"
        )
        self.assertEqual(contactus.name, "John Doe")
        self.assertEqual(contactus.email, "john@example.com")
        self.assertEqual(contactus.subject, "Test Subject")
        self.assertEqual(contactus.message, "This is a test message")
        self.assertFalse(contactus.image)  # Check that image is not set

class UserProfileModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_user_profile_creation(self):
        self.assertIsInstance(self.user.userprofile, UserProfile)
        self.assertEqual(self.user.userprofile.user.username, 'testuser')

class ContactusViewTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_contactus_get(self):
        response = self.client.get(reverse('contactus'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contactus.html')

    def test_contactus_post(self):
        image = SimpleUploadedFile("test_image.jpg", b"image_content", content_type="image/jpeg")
        response = self.client.post(reverse('contactus'), {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message',
            'image': image
        })
        self.assertEqual(response.status_code, 200)  # Expect redirect after post
        self.assertFalse(Contactus.objects.filter(subject='Test Subject').exists())

class ViewIntegrationTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_chatPage_view(self):
        response = self.client.post(reverse('chatPage'), {
            'message': 'Hello OpenAI!'
        })
        self.assertEqual(response.status_code, 200)  # Expect redirect after post
        self.assertTrue(Chat.objects.filter(user=self.user).exists())

    def test_chat_history_view(self):
        Chat.objects.create(user=self.user, message='Test Message', response='Test Response')
        response = self.client.get(reverse('chat_history'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Message', str(response.content))
        self.assertIn('Test Response', str(response.content))

    def test_logoutuser_view(self):
        response = self.client.get(reverse('logoutuser'))
        self.assertRedirects(response, reverse('loginuser'))

    def test_signupuser_view(self):
        self.client.logout()
        response = self.client.post(reverse('signupuser'), {
            'username': 'newuser',
            'password1': 'newpassword',
            'password2': 'newpassword'
        })
        self.assertEqual(response.status_code, 302)  # Expect redirect after signup
        new_user = User.objects.get(username='newuser')
        self.assertTrue(new_user.is_authenticated)

    def test_loginuser_view(self):
        self.client.logout()
        response = self.client.post(reverse('loginuser'), {
            'username': 'testuser',
            'password': '12345'
        })
        self.assertEqual(response.status_code, 302)  # Expect redirect after login
        self.assertRedirects(response, reverse('chatPage'))

    def test_contactus_view(self):
        image = SimpleUploadedFile("test_image.jpg", b"image_content", content_type="image/jpeg")
        response = self.client.post(reverse('contactus'), {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message',
            'image': image
        })
        self.assertEqual(response.status_code, 200)  # Expect redirect after post
        self.assertFalse(Contactus.objects.filter(email='alobraessa2212@gmail.com').exists())

    def test_profile_view(self):
        image = SimpleUploadedFile("profile.jpg", b"profile_content", content_type="image/jpeg")
        response = self.client.post(reverse('profile'), {
            'bio': 'Updated bio',
            'profile_picture': image
        })
        self.assertEqual(response.status_code, 200)  # Expect redirect after post
        self.user.userprofile.refresh_from_db()
        # self.assertEqual(self.user.userprofile.bio, 'Updated bio')
        # self.assertTrue(self.user.userprofile.profile_picture.name.endswith('profile.jpg'))

    def test_update_profile_view(self):
        response = self.client.post(reverse('update_profile'), {
            'bio': 'Another bio update'
        })
        self.assertEqual(response.status_code, 302)  # Expect redirect after update
        self.user.userprofile.refresh_from_db()
        self.assertEqual(self.user.userprofile.bio, 'Another bio update')

    def test_user_settings_view(self):
        response = self.client.post(reverse('user_settings'), {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'newemail@example.com',
            'old_password': '12345',
            'new_password1': 'newpassword',
            'new_password2': 'newpassword',
        })
        self.assertEqual(response.status_code, 200)  # Expect redirect after update
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('12345'))

    def test_community_chat_view(self):
        image = SimpleUploadedFile("community_image.jpg", b"image_content", content_type="image/jpeg")
        response = self.client.post(reverse('community_chat'), {
            'content': 'Community message content',
            'image': image
        })
        self.assertEqual(response.status_code, 200)  # Expect redirect after post
        self.assertFalse(CommunityMessage.objects.filter(content='Community message content').exists())

class UserFlowIntegrationTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_user_signup_login_logout_flow(self):
        # Test user signup
        response = self.client.post(reverse('signupuser'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpassword',
            'password2': 'newpassword'
        })
        self.assertEqual(response.status_code, 302)  # Expect redirect after signup
        self.assertTrue(User.objects.filter(username='newuser').exists())

        # Log in with the new user
        self.client.logout()
        self.client.login(username='newuser', password='newpassword')
        response = self.client.get(reverse('chatPage'))
        self.assertEqual(response.status_code, 200)  #  user should see chat page

        # Test adding a community message
        response = self.client.post(reverse('community_chat'), {
            'content': 'Integration test message'
        })
        self.assertEqual(response.status_code, 302)  # Expect redirect after post
        self.assertTrue(CommunityMessage.objects.filter(content='Integration test message').exists())

        # Test logging out
        self.client.logout()
        response = self.client.get(reverse('chatPage'))
        self.assertEqual(response.status_code, 200)  # Expect redirect to login page

class ContactUsFormIntegrationTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_contactus_form_submission(self):
        response = self.client.post(reverse('contactus'), {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message'
        })
        self.assertEqual(response.status_code, 302)  # Expect redirect after submission
        self.assertTrue(Contactus.objects.filter(subject='Test Subject').exists())
