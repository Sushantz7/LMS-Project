from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import CustomUser
from courses.models import Course, CourseProgress, Enrollment, Certificate, CourseReview

class CourseTests(APITestCase):
    def setUp(self):
        self.instructor = CustomUser.objects.create_user(username="instructor", password="pass", role="instructor", email="instructor@test.com")
        self.student = CustomUser.objects.create_user(username="student", password="pass", role="student", email="student@test.com")
        self.course = Course.objects.create(title="Test Course", description="Sample", instructor=self.instructor)

    def authenticate(self, user):
        response = self.client.post(reverse("login"), {
            "username": user.username,
            "password": "pass"
        })
        self.assertEqual(response.status_code, 200)
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


    def test_create_course(self):
        self.authenticate(self.instructor)
        url = reverse("create-course")
        data = {
            "title": "New Course",
            "description": "Course Desc",
            "difficulty": "beginner"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_enroll_course(self):
        self.authenticate(self.student)
        url = reverse("enroll_course", args=[self.course.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Enrollment.objects.filter(student=self.student, course=self.course).exists())

    def test_mark_lesson_completed(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        self.authenticate(self.student)
        url = reverse("mark-lesson-completed", args=[self.course.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(float(response.data["progress"]), 0)

    def test_generate_certificate_success(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        CourseProgress.objects.create(student=self.student, course=self.course, completion_percentage=100.0)
        self.authenticate(self.student)
        url = reverse("generate-certificate", args=[self.course.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("certificate_url", response.data)

    def test_submit_review_requires_enrollment(self):
        self.authenticate(self.student)
        url = reverse("submit-course-review", args=[self.course.id])
        data = {"rating": 4, "review_text": "Nice"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_reviews_authenticated(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        CourseReview.objects.create(course=self.course, student=self.student, rating=4, review_text="Nice")
        self.authenticate(self.student)
        url = reverse("get-course-reviews", args=[self.course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
