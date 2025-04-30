from rest_framework import serializers
from .models import Course, Enrollment, Assessment, AssessmentResult,CourseProgress, Certificate, CourseReview,StudentSubmission

class CourseSerializer(serializers.ModelSerializer):
    instructor = serializers.StringRelatedField(read_only=True)  # Show instructor's username instead of ID
    students = serializers.StringRelatedField(many=True, read_only=True)  # Show enrolled students' usernames

    class Meta:
        model = Course
        fields = ["id", "title", "description", "instructor", "difficulty", "students", "created_at"]
        read_only_fields = ["instructor", "created_at"] 
class EnrollmentSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "student", "course", "enrolled_at"]
        read_only_fields = ["student", "enrolled_at"]


class AssessmentResultSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField(read_only=True)
    assessment = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AssessmentResult
        fields = ["id", "student", "assessment", "score", "submitted_at"]
        read_only_fields = ["student", "submitted_at"]


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'

class CourseReviewSerializer(serializers.ModelSerializer):
    student = serializers.ReadOnlyField(source='student.username')  # Display student username
    course = serializers.ReadOnlyField(source='course.title')  # Display course title

    class Meta:
        model = CourseReview
        fields = ['rating',  'review_text', 'student', 'course']

class CourseProgressSerializer(serializers.ModelSerializer):
    student = serializers.ReadOnlyField(source='student.username')
    course = serializers.ReadOnlyField(source='course.title')

    class Meta:
        model = CourseProgress
        fields = '__all__'


class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ['id', 'course', 'title', 'description', 'due_date']

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSubmission
        fields = ['id', 'assessment', 'student', 'content', 'submitted_at', 'grade']
        read_only_fields = ['student', 'submitted_at', 'grade']