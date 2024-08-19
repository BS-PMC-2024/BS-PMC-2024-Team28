from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import Client
from .models import CommunityMessage, Contactus, UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile

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
        self.assertFalse(message.image)  # Updated check

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
        self.assertFalse(contactus.image)  # Updated check

class UserProfileModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_user_profile_creation(self):
        self.assertIsInstance(self.user.userprofile, UserProfile)
        self.assertEqual(self.user.userprofile.user.username, 'testuser')

class CommunityChatViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_community_chat_get(self):
        response = self.client.get(reverse('community_chat'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'community_chat.html')

    def test_community_chat_post(self):
        response = self.client.post(reverse('community_chat'), {
            'content': 'Test message content'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after post
        self.assertTrue(CommunityMessage.objects.filter(content='Test message content').exists())

class ContactusViewTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_contactus_get(self):
        response = self.client.get(reverse('contactus'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contactus.html')

    def test_contactus_post(self):
        response = self.client.post(reverse('contactus'), {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message'
        })
        self.assertEqual(response.status_code, 200)  # Renders the form again
        self.assertTrue(Contactus.objects.filter(subject='Test Subject').exists())
        self.assertContains(response, 'Message was sent successfully')




class ContactUsFormIntegrationTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_contactus_form_submission(self):
        response = self.client.post(reverse('contactus'), {
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'subject': 'Integration Test Subject',
            'message': 'This is an integration test message'
        })
        self.assertEqual(response.status_code, 200)  # Form should be rendered again
        self.assertTrue(Contactus.objects.filter(subject='Integration Test Subject').exists())
        self.assertContains(response, 'Message was sent successfully')





