
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny  # For local prototype velocity
from django.shortcuts import get_object_or_404
from .models import EmissionActivityRecord
from .serializers import EmissionActivityRecordSerializer


class EmissionLedgerViewSet(viewsets.ModelViewSet):
    """
    Exposes full list, details, filtering, and manual audit-approvals 
    for the single source of truth emission records.
    """
    queryset = EmissionActivityRecord.objects.all().order_by('-activity_start_date')
    serializer_class = EmissionActivityRecordSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Enables advanced pipeline filtering:
        e.g., /api/ledger/?status=SUSPICIOUS
        e.g., /api/ledger/?scope=SCOPE_1
        """
        queryset = self.queryset
        validation_status = self.request.query_params.get('status')
        scope = self.request.query_params.get('scope')

        if validation_status:
            queryset = queryset.filter(validation_status=validation_status)
        if scope:
            queryset = queryset.filter(scope_category=scope)
        return queryset

    @action(detail=True, methods=['post'], url_path='approve-record')
    def approve_record(self, request, pk=None):
        """
        Custom execution endpoint. When clicked, signs off on data 
        integrity anomalies and triggers system immutability lock.
        """
        record = self.get_object()


        from django.contrib.auth.models import User
        mock_analyst = User.objects.first() or User.objects.create_user(username="compliance_officer_1")

        try:
            record.transition_to_approved(mock_analyst)
            return Response(
                {"status": "Record signed off and permanently locked for audit integrity."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )