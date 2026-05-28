
from rest_framework import serializers
from .models import EmissionActivityRecord, IngestionJobLog, Organization

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'created_at']

class IngestionJobLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngestionJobLog
        fields = ['id', 'source_type', 'filename', 'created_at']

class EmissionActivityRecordSerializer(serializers.ModelSerializer):

    job_source_details = IngestionJobLogSerializer(source='job_source', read_only=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True)

    class Meta:
        model = EmissionActivityRecord
        fields = [
            'id', 'scope_category', 'ghg_mapping_category',
            'original_quantity', 'original_unit', 'normalized_quantity_co2e',
            'activity_start_date', 'activity_end_date', 'validation_status',
            'validation_notes', 'approval_status', 'is_locked',
            'approved_by_username', 'approved_at', 'job_source_details'
        ]
        read_only_fields = ['is_locked', 'normalized_quantity_co2e', 'approved_at']