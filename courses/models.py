from django.db import models
from users.models import CustomUser
from django.utils import timezone

class Course(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='courses',limit_choices_to={'role': 'instructor'})
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES,default='beginner')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} -> {self.course.title}"

# class Assessment(models.Model):
#     course = models.ForeignKey(Course, on_delete=models.CASCADE)
#     title = models.CharField(max_length=255)
#     max_score = models.IntegerField()
#     due_date = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"{self.title} ({self.course.title})"
class Assessment(models.Model):
    course = models.ForeignKey(Course, related_name='assessments', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)  # Optional description field
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class AssessmentResult(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    score = models.IntegerField()
    submitted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.username} - {self.assessment.title}: {self.score}"
    

class CourseProgress(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="progress")
    completed_lessons = models.IntegerField(default=0)  # Tracks number of completed lessons
    total_lessons = models.IntegerField(default=0)  # Stores total lessons in course
    progress_percentage = models.FloatField(default=0.0)  # Progress percentage
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Completion percentage
    last_updated = models.DateTimeField(auto_now=True)  # Auto-updated timestamp

    class Meta:
        unique_together = ('student', 'course')

    def update_progress(self):
        """Update progress percentage based on completed lessons"""
        if self.total_lessons > 0:
            self.progress_percentage = (self.completed_lessons / self.total_lessons) * 100
            self.completion_percentage = round(self.progress_percentage, 2)
        else:
            self.progress_percentage = 0
            self.completion_percentage = 0.00
        self.save()

    def __str__(self):
        return f"{self.student.username} - {self.course.title}: {self.completion_percentage}%"

class Certificate(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_url = models.URLField(blank=True, null=True)  # Link to the certificate PDF

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"Certificate: {self.student.username} - {self.course.title}"


class CourseReview(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField()  # Rating out of 5
    review_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')  # Prevent duplicate reviews

    def __str__(self):
        return f"Review: {self.student.username} -> {self.course.title} ({self.rating}/5)"
    
from courses.models import Course


class StudentSubmission(models.Model):
    assessment = models.ForeignKey(Assessment, related_name='submissions', on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    content = models.TextField(blank=True, null=True)  # optional: you can change it to FileField if you want file uploads
    submitted_file = models.FileField(upload_to='submissions/')  # optional: you can change it to TextField if you want text answers
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # instructor can assign grades

    def __str__(self):
        return f"{self.student.username} - {self.assessment.title}"
