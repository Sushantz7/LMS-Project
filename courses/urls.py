from django.urls import path,include
from .views import create_course, enroll_course, CourseViewSet, EnrollmentCreateView, CourseListView, get_course_progress, update_course_progress, mark_lesson_completed, generate_certificate, get_course_reviews, submit_review, SponsorDashboardMetricsView, AdminDashboardMetricsView, InstructorDashboardView, sponsor_dashboard,admin_dashboard, send_deadline_reminder, send_instructor_course_summary,create_assessment, submit_assessment, grade_submission, list_assessments, list_submissions

urlpatterns = [
    path("create/", create_course, name="create-course"),
    path("<int:course_id>/enroll/", enroll_course, name="enroll_course"),
    path('', CourseListView.as_view(), name='course-list'),
    path('<int:course_id>/progress/', get_course_progress, name="get-course-progress"),
    path('<int:course_id>/progress/update/', update_course_progress, name="update-course-progress"),
    path('<int:course_id>/mark-complete/', mark_lesson_completed, name="mark-lesson-completed"),
    path('<int:course_id>/certificate/', generate_certificate, name="generate-certificate"),
    path('<int:course_id>/reviews/', get_course_reviews, name="get-course-reviews"),
    path('<int:course_id>/reviews/submit/', submit_review, name="submit-course-review"),
    path("sponsor/metrics/", SponsorDashboardMetricsView.as_view(), name="sponsor-dashboard-metrics"),
    path("admin/metrics/", AdminDashboardMetricsView.as_view(), name="admin-dashboard-metrics"),
    path("instructor/metrics/", InstructorDashboardView.as_view(), name="instructor-dashboard-metrics"),
    path('sponsor/dashboard/', sponsor_dashboard, name="sponsor-dashboard"),
    path("admin/dashboard/", admin_dashboard, name="admin-dashboard"),
    path("<int:pk>/send-reminder/", send_deadline_reminder, name="send-deadline-reminder"),
    path("instructor/send-summary/", send_instructor_course_summary, name="send-instructor-summary"), 
    path('<int:course_id>/assessments/create/', create_assessment, name='create-assessment'),
    path('<int:assessment_id>/assessments/submit/', submit_assessment, name='submit-assessment'),
    path('submissions/<int:submission_id>/grade/', grade_submission, name='grade-submission'),
    path("<int:course_id>/assessments/", list_assessments, name="list-assessments"),
    path("assessments/<int:assessment_id>/submissions/", list_submissions, name="list-submissions"),

]

