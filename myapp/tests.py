from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import  Contactus

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