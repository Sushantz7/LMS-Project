from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import CustomUser

class UserAuthTests(APITestCase):

    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.profile_url = reverse("profile")
        self.admin_dashboard_url = reverse("admin-dashboard")

        self.student_data = {
            "username": "student1",
            "email": "student1@example.com",
            "password": "testpass123",
            "role": "student"
        }

        self.admin_data = {
            "username": "admin1",
            "email": "admin1@example.com",
            "password": "adminpass123",
            "role": "admin"
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.student_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().role, "student")

    def test_login_and_get_token(self):
        self.client.post(self.register_url, self.student_data)
        response = self.client.post(self.login_url, {
            "username": "student1",
            "password": "testpass123"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_profile_access(self):
        self.client.post(self.register_url, self.student_data)
        login = self.client.post(self.login_url, {
            "username": "student1",
            "password": "testpass123"
        })
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + login.data["access"])
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_dashboard_access_denied_for_student(self):
        self.client.post(self.register_url, self.student_data)
        login = self.client.post(self.login_url, {
            "username": "student1",
            "password": "testpass123"
        })
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + login.data["access"])
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_dashboard_access_allowed_for_admin(self):
        self.client.post(self.register_url, self.admin_data)
        CustomUser.objects.filter(email="admin1@example.com").update(is_staff=True)

        login = self.client.post(self.login_url, {
            "username": "admin1",
            "password": "adminpass123"
        })
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + login.data["access"])
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
