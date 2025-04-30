from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import CustomUser
from sponsorships.models import Sponsorship
from courses.models import Course, Enrollment, CourseProgress


class SponsorshipTests(APITestCase):
    def setUp(self):
        self.sponsor = CustomUser.objects.create_user(username="sponsor", password="pass", role="sponsor", email="sponsor@example.com")
        self.student = CustomUser.objects.create_user(username="student", password="pass", role="student", email="student@example.com")
        self.course = Course.objects.create(title="Sponsored Course", description="Desc", instructor=self.sponsor, difficulty="beginner")
        Enrollment.objects.create(student=self.student, course=self.course)
        CourseProgress.objects.create(student=self.student, course=self.course, completion_percentage=80.0)

    def authenticate(self):
        response = self.client.post(reverse("login"), {
            "username": self.sponsor.username,
            "password": "pass"
        })
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_sponsorship(self):
        self.authenticate()
        data = {
            "student": self.student.id,
            "funding_amount": "100.00"
        }
        response = self.client.post(reverse("create-sponsorship"), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_sponsorship_blocked(self):
        Sponsorship.objects.create(sponsor=self.sponsor, student=self.student, funding_amount="100.00")
        self.authenticate()
        data = {
            "student": self.student.id,
            "funding_amount": "100.00"
        }
        response = self.client.post(reverse("create-sponsorship"), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dashboard_view(self):
        Sponsorship.objects.create(sponsor=self.sponsor, student=self.student, funding_amount="100.00")
        self.authenticate()
        response = self.client.get(reverse("sponsor-dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("progress", response.data)

    def test_send_progress_email(self):
        Sponsorship.objects.create(sponsor=self.sponsor, student=self.student, funding_amount="100.00")
        self.authenticate()
        response = self.client.post(reverse("send-sponsor-progress"))
        self.assertEqual(response.status_code, 200)
