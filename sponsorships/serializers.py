from rest_framework import serializers
from .models import Sponsorship, SponsorshipRequest

class SponsorshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sponsorship
        fields = ["id", "sponsor", "student", "funding_amount", "status"]
        read_only_fields = ["sponsor", "created_at"]

    def validate_funding_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Funding amount must be greater than zero.")
        return value

class SponsorshipRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SponsorshipRequest
        fields = ['id', 'student', 'course', 'message', 'status', 'requested_at']
        read_only_fields = ['student', 'status', 'requested_at']
