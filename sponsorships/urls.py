from django.urls import path
from .views import create_sponsorship,SponsorshipListCreateView, sponsor_dashboard, send_sponsor_progress_email, request_sponsorship, list_sponsorship_requests

urlpatterns = [
    path("sponsor/", create_sponsorship, name="create-sponsorship"),
    path('', SponsorshipListCreateView.as_view(), name='sponsorships-list'),
    path("dashboard/", sponsor_dashboard, name="sponsor-dashboard"),
    path("send-progress-report/", send_sponsor_progress_email, name="send-sponsor-progress"),
    path('request/', request_sponsorship, name='request-sponsorship'),
    path("requests/", list_sponsorship_requests, name="sponsorship-requests"),
]
