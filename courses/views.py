from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Course,Enrollment,CourseProgress,Certificate,CourseReview,Assessment,StudentSubmission
from .serializers import CourseSerializer, EnrollmentSerializer, CourseReviewSerializer, CourseProgressSerializer, AssessmentSerializer, SubmissionSerializer
from users.permissions import IsInstructor, IsStudent
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import viewsets,generics
from rest_framework.pagination import PageNumberPagination
from django.core.mail import send_mail 
from users.models import Notification
from rest_framework.views import APIView
from rest_framework import status
from users.models import CustomUser
from django.db.models import Avg
from rest_framework.exceptions import PermissionDenied
from users.permissions import IsSponsor

# ✅ Instructors Can Create Courses

@api_view(["POST"])
@permission_classes([IsAuthenticated, IsInstructor])
def create_course(request):
    serializer = CourseSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(instructor=request.user)  # Automatically set the instructor
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

# ✅ Students Can Enroll in Courses
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStudent])
def enroll_course(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response({"message": "Already enrolled."}, status=200)

        Enrollment.objects.create(student=request.user, course=course)
        Notification.objects.create(
            user=course.instructor,
            message=f"{request.user.username} enrolled in your course '{course.title}'",
            notification_type="course_update"
        )

        return Response({"message": "Enrolled successfully!"}, status=201)
    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=404)



class CourseListView(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["title", "instructor__username"]  # Search by course name or instructor
    filterset_fields = ["difficulty_level"]  # Filter by difficulty level
    ordering_fields = ["created_at"]  # Order by created_at date


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsInstructor]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title', 'difficulty', 'instructor']

class EnrollmentCreateView(generics.CreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

class CoursePagination(PageNumberPagination):
    page_size = 5  # Adjust page size as needed
    page_size_query_param = 'page_size'
    max_page_size = 20


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStudent])
def mark_lesson_completed(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        progress, created = CourseProgress.objects.get_or_create(student=request.user, course=course)
        
        # Assume each lesson contributes equally to course completion
        if progress.completion_percentage < 100:
            progress.completion_percentage = min(progress.completion_percentage + 10, 100)  # Adjust as needed
            progress.save()
            return Response({"message": "Lesson marked as completed!", "progress": progress.completion_percentage}, status=200)
        else:
            return Response({"error": "All lessons already completed!"}, status=400)

    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=404)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStudent])
def generate_certificate(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        progress = CourseProgress.objects.get(student=request.user, course=course)

        if progress.completion_percentage == 100:
            certificate, created = Certificate.objects.get_or_create(student=request.user, course=course)
            if created or not certificate.certificate_url:
                certificate.certificate_url = f"https://certificates.example.com/{certificate.id}.pdf"
                certificate.save()
            return Response({"certificate_url": certificate.certificate_url}, status=201)
        return Response({"error": "Progress not found. Complete lessons first!"}, status=400)

    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=404)
    except CourseProgress.DoesNotExist:
        return Response({"error": "Progress not found. Complete lessons first!"}, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStudent])
def submit_review(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response({"error": "You must be enrolled to review this course!"}, status=403)

        serializer = CourseReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=request.user, course=course)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)

    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=404)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_course_reviews(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        reviews = CourseReview.objects.filter(course=course)
        serializer = CourseReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=200)

    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=404)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsStudent])
def update_course_progress(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response({"error": "You must be enrolled in the course!"}, status=403)

        progress, created = CourseProgress.objects.get_or_create(student=request.user, course=course)
        new_progress = request.data.get("completion_percentage", progress.completion_percentage)

        if not (0 <= float(new_progress) <= 100):
            return Response({"error": "Completion percentage must be between 0 and 100."}, status=400)

        progress.completion_percentage = new_progress
        progress.save()

        # ✅ Notify instructor if completed
        if float(progress.completion_percentage) == 100:
            Notification.objects.create(
                user=course.instructor,
                message=f"{request.user.username} completed your course: {course.title}",
                notification_type="course_update"
            )

        return Response(CourseProgressSerializer(progress).data, status=200)

    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=404)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_course_progress(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        progress = CourseProgress.objects.filter(course=course, student=request.user).first()

        if progress:
            serializer = CourseProgressSerializer(progress)
            return Response(serializer.data, status=200)
        else:
            return Response({"message": "No progress found for this user in the course"}, status=200)

    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=404)


# File: courses/views.py

class SponsorDashboardMetricsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "sponsor":
            raise PermissionDenied("Only sponsors can access this data.")

        sponsored_students = CustomUser.objects.filter(sponsored_by=request.user)

        student_ids = sponsored_students.values_list('id', flat=True)

        total_students = sponsored_students.count()
        total_enrollments = Enrollment.objects.filter(student_id__in=student_ids).count()
        avg_progress = CourseProgress.objects.filter(student_id__in=student_ids).aggregate(avg=Avg('completion_percentage'))['avg'] or 0.0
        total_certificates = Certificate.objects.filter(student_id__in=student_ids).count()

        return Response({
            "total_students": total_students,
            "total_enrollments": total_enrollments,
            "average_progress": round(avg_progress, 2),
            "total_certificates": total_certificates,
        }, status=status.HTTP_200_OK)

# File: courses/views.py

class AdminDashboardMetricsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "admin":
            raise PermissionDenied("Only admins can access this data.")

        return Response({
            "total_users": CustomUser.objects.count(),
            "total_courses": Course.objects.count(),
            "total_enrollments": Enrollment.objects.count(),
            "total_certificates": Certificate.objects.count(),
            "total_instructors": CustomUser.objects.filter(role="instructor").count(),
            "total_students": CustomUser.objects.filter(role="student").count(),
            "total_sponsors": CustomUser.objects.filter(role="sponsor").count(),
            "average_progress": round(CourseProgress.objects.aggregate(avg=Avg("completion_percentage"))["avg"] or 0.0, 2)
        }, status=status.HTTP_200_OK)

# File: courses/views.py

class InstructorDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "instructor":
            raise PermissionDenied("Only instructors can access this data.")

        instructor = request.user
        courses = Course.objects.filter(instructor=instructor)
        course_ids = courses.values_list("id", flat=True)

        total_courses = courses.count()
        total_enrollments = Enrollment.objects.filter(course_id__in=course_ids).count()
        total_certificates = Certificate.objects.filter(course_id__in=course_ids).count()
        avg_progress = CourseProgress.objects.filter(course_id__in=course_ids).aggregate(avg=Avg("completion_percentage"))["avg"] or 0.0

        return Response({
            "total_courses": total_courses,
            "total_enrollments": total_enrollments,
            "total_certificates": total_certificates,
            "average_progress": round(avg_progress, 2)
        }, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsSponsor])
def sponsor_dashboard(request):
    sponsor = request.user
    sponsored_students = CustomUser.objects.filter(role='student')

    data = []
    for student in sponsored_students:
        student_data = {
            "student": student.username,
            "email": student.email,
            "progress": []
        }

        progresses = CourseProgress.objects.filter(student=student)
        for progress in progresses:
            student_data["progress"].append({
                "course": progress.course.title,
                "completion_percentage": float(progress.completion_percentage),
                "last_updated": progress.last_updated
            })

        data.append(student_data)

    return Response(data, status=200)


from users.permissions import IsAdmin  # Ensure this exists or create it

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdmin])
def admin_dashboard(request):
    data = {
        "total_users": {
            "students": CustomUser.objects.filter(role='student').count(),
            "instructors": CustomUser.objects.filter(role='instructor').count(),
            "sponsors": CustomUser.objects.filter(role='sponsor').count(),
            "admins": CustomUser.objects.filter(role='admin').count(),
        },
        "total_courses": Course.objects.count(),
        "total_enrollments": Enrollment.objects.count(),
        "average_completion_percentage": round(
            CourseProgress.objects.aggregate(avg=Avg("completion_percentage"))["avg"] or 0.0, 2
        )
    }
    return Response(data, status=200)


@api_view(["POST"]) 
@permission_classes([IsAuthenticated, IsInstructor]) 
def send_deadline_reminder(request, pk): 
    try: 
        course = Course.objects.get(pk=pk, instructor=request.user)

        enrollments = Enrollment.objects.filter(course=course)
        students = [enrollment.student for enrollment in enrollments]
        for student in students:
            send_mail(
                subject=f"Reminder: Deadline approaching for {course.title}",
                message=f"Dear {student.username},\n\nThis is a reminder that the deadline for {course.title} is coming up soon. Make sure to complete your lessons and assessments!",
                from_email="your_email@gmail.com",                  # use the same email as in EMAIL_HOST_USER
                recipient_list=[student.email],
                fail_silently=False
            )

        return Response({"message": f"Reminder email sent to {len(students)} students."}, status=200)

    except Course.DoesNotExist:
        return Response({"error": "Course not found or you are not the instructor."}, status=404)


@api_view(["POST"]) 
@permission_classes([IsAuthenticated, IsInstructor]) 
def send_instructor_course_summary(request): 
    if request.user.role != "instructor": 
        return Response({"error": "Only instructors can send course summaries."}, status=403)

    courses = Course.objects.filter(instructor=request.user)
    if not courses.exists():
        return Response({"message": "You have no courses."}, status=200)

    email_body = f"Course Completion Report for {request.user.username}\n\n"

    for course in courses:
        progresses = CourseProgress.objects.filter(course=course)
        total_students = progresses.count()
        completed = progresses.filter(completion_percentage=100).count()
        avg_completion = (
            sum(float(p.completion_percentage) for p in progresses) / total_students
            if total_students > 0 else 0
        )

        email_body += (
            f"Course: {course.title}\n"
            f" - Enrolled Students: {total_students}\n"
            f" - Completed: {completed}\n"
            f" - Avg Completion: {avg_completion:.2f}%\n\n"
        )

    send_mail(
        subject="Your Course Summary Report",
        message=email_body,
        from_email="your_email@gmail.com",
        recipient_list=[request.user.email],
        fail_silently=False,
    )

    return Response({"message": "Summary email sent successfully!"}, status=200)



# Instructor creates an assessment
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsInstructor])
def create_assessment(request, course_id):
    try:
        course = Course.objects.get(id=course_id, instructor=request.user)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found or you are not the instructor.'}, status=404)
    
    serializer = AssessmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(course=course)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

# Student submits an assignment
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStudent])
def submit_assessment(request, assessment_id):
    try:
        assessment = Assessment.objects.get(id=assessment_id)
    except Assessment.DoesNotExist:
        return Response({'error': 'Assessment not found.'}, status=404)

    serializer = SubmissionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(student=request.user, assessment=assessment)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

# Instructor grades a submission
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsInstructor])
def grade_submission(request, submission_id):
    try:
        submission = StudentSubmission.objects.get(id=submission_id)
        if submission.assessment.course.instructor != request.user:
            return Response({'error': 'You are not authorized to grade this submission.'}, status=403)
    except StudentSubmission.DoesNotExist:
        return Response({'error': 'Submission not found.'}, status=404)
    
    grade = request.data.get('grade')
    if not grade:
        return Response({'error': 'Grade is required.'}, status=400)
    
    submission.grade = grade
    submission.save()
    return Response({'message': 'Submission graded successfully.'}, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsInstructor])
def list_assessments(request, course_id):
    try:
        course = Course.objects.get(id=course_id, instructor=request.user)
        assessments = Assessment.objects.filter(course=course)
        serializer = AssessmentSerializer(assessments, many=True)
        return Response(serializer.data, status=200)

    except Course.DoesNotExist:
        return Response({"error": "Course not found or you are not the instructor."}, status=404)

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsInstructor])
def list_submissions(request, assessment_id):
    try:
        assessment = Assessment.objects.get(id=assessment_id, course__instructor=request.user)
        submissions = StudentSubmission.objects.filter(assessment=assessment)
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data, status=200)

    except Assessment.DoesNotExist:
        return Response({"error": "Assessment not found or you are not the instructor."}, status=404)
