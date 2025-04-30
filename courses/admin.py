from django.contrib import admin
from courses.models import Course, Enrollment,Assessment,AssessmentResult,CourseProgress,Certificate,CourseReview

admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(Assessment)
admin.site.register(AssessmentResult)
admin.site.register(CourseProgress)
admin.site.register(Certificate)
admin.site.register(CourseReview)