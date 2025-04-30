from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from users.permissions import IsSponsor,IsStudent
from .models import Sponsorship,SponsorshipRequest
from .serializers import SponsorshipSerializer, SponsorshipRequestSerializer
from rest_framework import generics
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from users.models import Notification 
from django.core.mail import send_mail 
from users.models import CustomUser 
from courses.models import CourseProgress

@api_view(["POST"])
@permission_classes([IsSponsor])
def create_sponsorship(request):
    student_id = request.data.get("student")

    if Sponsorship.objects.filter(sponsor=request.user, student_id=student_id).exists():
        return Response({"error": "Sponsorship already exists!"}, status=400)

    serializer = SponsorshipSerializer(data=request.data)
    if serializer.is_valid():
        sponsorship = serializer.save(sponsor=request.user)

        # ✅ Notify student
        Notification.objects.create(
            user=sponsorship.student,
            message=f"You have been funded by {request.user.username}!",
            notification_type="sponsorship_update"
        )

        return Response(serializer.data, status=201)
    
    return Response(serializer.errors, status=400)


class SponsorshipListCreateView(generics.ListCreateAPIView):
    queryset = Sponsorship.objects.all()
    serializer_class = SponsorshipSerializer
    permission_classes = [IsAuthenticated, IsSponsor]
    filterset_fields = ['student']

class SponsorshipPagination(PageNumberPagination):
    page_size = 5  
    page_size_query_param = 'page_size'
    max_page_size = 20

class SponsorshipListView(ListAPIView):

    queryset = Sponsorship.objects.all()
    serializer_class = SponsorshipSerializer
    pagination_class = SponsorshipPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['student__status', 'student__progress']


@api_view(["GET"])
@permission_classes([IsAuthenticated,IsSponsor])
def sponsor_dashboard(request):
    if request.user.role != "sponsor":
        return Response({"error": "Access denied. Only sponsors allowed."}, status=403)

    sponsored_students = CustomUser.objects.filter(sponsorships__sponsor=request.user).distinct()

    progress_data = []
    for student in sponsored_students:
        progress_entries = CourseProgress.objects.filter(student=student)
        for p in progress_entries:
            progress_data.append({
                "student": student.username,
                "course": p.course.title,
                "completion_percentage": float(p.completion_percentage)
            })

    response = {
        "sponsored_students": sponsored_students.count(),
        "progress": progress_data
    }
    return Response(response, status=200)



@api_view(["POST"]) 
@permission_classes([IsAuthenticated, IsSponsor]) 
def send_sponsor_progress_email(request): 
    if request.user.role != "sponsor": 
        return Response({"error": "Only sponsors can request progress emails."}, status=403)
    
    sponsored_students = CustomUser.objects.filter(sponsorships__sponsor=request.user).distinct()

    if not sponsored_students.exists():
        return Response({"message": "You are not sponsoring any students."}, status=200)

    # Construct the email body
    email_body = f"Progress Report for Sponsor: {request.user.username}\n\n"

    for student in sponsored_students:
        progresses = CourseProgress.objects.filter(student=student)
        email_body += f"Student: {student.username}\n"
        for progress in progresses:
            email_body += f"  - Course: {progress.course.title} | Completion: {progress.completion_percentage}%\n"
        email_body += "\n"

    send_mail(
        subject="Sponsored Students Progress Report",
        message=email_body,
        from_email="your_email@gmail.com",
        recipient_list=[request.user.email],
        fail_silently=False,
    )

    return Response({"message": "Progress report email sent successfully!"}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStudent])
def request_sponsorship(request):
    serializer = SponsorshipRequestSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(student=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsSponsor])
def list_sponsorship_requests(request):
    requests = SponsorshipRequest.objects.filter(status='pending')
    serializer = SponsorshipRequestSerializer(requests, many=True)
    return Response(serializer.data)