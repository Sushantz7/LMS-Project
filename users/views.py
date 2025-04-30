from django.contrib.auth import authenticate,get_user_model
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from users.serializers import NotificationSerializer
from users.models import CustomUser,Notification
from courses.models import Course, Enrollment, Certificate, CourseReview, Assessment
from .permissions import IsAdmin

#Register User
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)  # Generate JWT Token
        
        return Response({
            "message": "User registered successfully!",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": user.role
        }, status=201)
    
    return Response(serializer.errors, status=400)


#Login (Token-Based)

@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": user.role
        })

    return Response({"error": "Invalid Credentials"}, status=400)


# Get User Profile
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user

    if user.role == "student":
        return Response({"message": "You are a student and students have limited profile access."})

    elif user.role == "instructor":
        return Response({"message": "Instructors can manage courses."})

    elif user.role == "admin":
        return Response({"message": "Admins have full access."})

    elif user.role == "sponsor":
        return Response({"message": "Sponsors can view funding information."})

    return Response({"error": "Invalid role."}, status=403)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
@permission_classes([IsAdmin])
def admin_dashboard(request):
    if request.user.role != "admin":
        return Response({"error": "Access denied. Only admin allowed."}, status=403)

    data = {
        "total_users": CustomUser.objects.count(),
        "students": CustomUser.objects.filter(role="student").count(),
        "instructors": CustomUser.objects.filter(role="instructor").count(),
        "sponsors": CustomUser.objects.filter(role="sponsor").count(),
        "courses": Course.objects.count(),
        "enrollments": Enrollment.objects.count(),
        "certificates": Certificate.objects.count(),
        "reviews": CourseReview.objects.count(),
        "assessments": Assessment.objects.count()
    }
    return Response(data, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data, status=200)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_notification_as_read(request, pk):
    try:
        notification = Notification.objects.get(id=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marked as read."}, status=200)
    except Notification.DoesNotExist:
        return Response({"error": "Notification not found."}, status=404)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    request.user.notifications.update(is_read=True)
    return Response({"message": "All notifications marked as read."}, status=200)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_notifications(request):
    """List notifications for the authenticated user (most recent first)."""
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_notification(request, pk):
    """Delete a notification belonging to the authenticated user."""
    try:
        notification = Notification.objects.get(id=pk, user=request.user)
        notification.delete()
        return Response({"message": "Notification deleted successfully."}, status=204)
    except Notification.DoesNotExist:
        return Response({"error": "Notification not found."}, status=404)
