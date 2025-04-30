from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
        ('sponsor', 'Sponsor'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES,default='student')
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)


    groups = models.ManyToManyField(
        Group,
        related_name="customuser_groups",  # Prevents conflict with default auth.User
        blank=True
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_permissions",  # Prevents conflict with default auth.User
        blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
    
    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     group, created = Group.objects.get_or_create(name=self.role)
    #     self.groups.add(group)

class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(
        max_length=50, 
        choices=[
            ('course_update', 'Course Update'),
            ('assessment_due', 'Assessment Due'),
            ('sponsorship_update', 'Sponsorship Update'),
            ('general', 'General Notification')
        ],
        default='general'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.message[:30]}..."
    

