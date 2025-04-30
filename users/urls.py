from django.urls import path
from users.views import register,login, profile,logout, admin_dashboard, user_notifications,mark_notification_as_read, mark_all_notifications_read,list_notifications,delete_notification

urlpatterns = [
    path("register/", register, name="register"),
    path('login/', login, name='login'),
    path("profile/", profile, name="profile"),
    path("logout/", logout, name="logout"),
    path("admin-dashboard/", admin_dashboard, name="admin-dashboard"),
    path("notifications/", user_notifications, name="user-notifications"),
    path("notifications/<int:pk>/read/", mark_notification_as_read, name="mark-notification-read"),
    path("notifications/mark-all-read/", mark_all_notifications_read, name="mark-all-read"),
    path("notifications/", list_notifications, name="notification-list"),
    path("notifications/<int:pk>/delete/", delete_notification, name="notification-delete"),

]
