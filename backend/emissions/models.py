import uuid
from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Organization(models.Model):
    """Handles multi-tenancy. Every client enterprise maps here."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class IngestionJobLog(models.Model):
    """Tracks data lineage. Tells auditors exactly where data originated."""
    SOURCE_CHOICES = [
        ('SAP', 'SAP ERP Procurement/Fuel File'),
        ('UTILITY', 'Utility Portal CSV Export'),
        ('TRAVEL', 'Corporate Travel Platform API/Webhook'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='ingestion_jobs')
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    filename = models.CharField(max_length=255, blank=True, null=True)
    raw_payload_backup = models.TextField(help_text="Stores the exact raw string or JSON input data.")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)


class EmissionActivityRecord(models.Model):
    """
    The Single Source of Truth Ledger. Stores normalized data mapped to 
    GHG accounting protocols with systemic lock mechanisms.
    """
    SCOPE_CHOICES = [
        ('SCOPE_1', 'Scope 1: Direct Emissions (e.g., Fuel Combustion)'),
        ('SCOPE_2', 'Scope 2: Indirect Emissions (e.g., Purchased Electricity)'),
        ('SCOPE_3', 'Scope 3: Value Chain (e.g., Business Travel, Procurement)'),
    ]

    VALIDATION_STATUS_CHOICES = [
        ('PENDING', 'Pending Validation Analysis'),
        ('VALID', 'Passed Structural Validation'),
        ('SUSPICIOUS', 'Flagged as Anomalous/Suspicious'),
        ('FAILED', 'Validation Failed (Unparseable/Missing data)'),
    ]

    APPROVAL_STATUS_CHOICES = [
        ('DRAFT', 'Draft / Unreviewed'),
        ('APPROVED', 'Approved & Locked for Audit'),
        ('REJECTED', 'Rejected / Excluded from Ledger'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, db_index=True)
    job_source = models.ForeignKey(IngestionJobLog, on_delete=models.PROTECT, related_name='records')


    scope_category = models.CharField(max_length=15, choices=SCOPE_CHOICES, db_index=True)
    ghg_mapping_category = models.CharField(max_length=100)


    original_quantity = models.DecimalField(max_digits=15, decimal_places=4)
    original_unit = models.CharField(max_length=50)


    normalized_quantity_co2e = models.DecimalField(max_digits=15, decimal_places=4, default=0.0000)


    activity_start_date = models.DateField(db_index=True)
    activity_end_date = models.DateField()

    # Pipeline Flags & Auditing Metadata
    validation_status = models.CharField(max_length=15, choices=VALIDATION_STATUS_CHOICES, default='PENDING',
                                         db_index=True)
    validation_notes = models.TextField(blank=True, null=True)

    approval_status = models.CharField(max_length=15, choices=APPROVAL_STATUS_CHOICES, default='DRAFT', db_index=True)
    is_locked = models.BooleanField(default=False, db_index=True)

    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='approved_records')
    approved_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        """
        Defensive verification framework. Ensures data cannot be altered once 
        the statutory lock state is established.
        """
        super().clean()


        if self._state.adding is False:
            original = EmissionActivityRecord.objects.get(pk=self.pk)
            if original.is_locked:
                raise ValidationError({
                    'approval_status': "Immutability Violation: This ledger line item has been verified and locked. Modifications are prohibited by audit protocol."
                })

        # Logical boundary constraints check
        if self.activity_start_date and self.activity_end_date:
            if self.activity_start_date > self.activity_end_date:
                raise ValidationError({
                    'activity_start_date': "Chronological Alignment Error: Activity start date cannot occur after the end date."
                })

    def save(self, *args, **kwargs):
        """Enforces clean context execution explicitly before hitting the SQL persistence layer."""
        self.full_clean()
        super().save(*args, **kwargs)

    def transition_to_approved(self, user):
        """
        Executes a secure atomic state-machine transition using database locks
        to completely neutralize race conditions.
        """
        with transaction.atomic():

            locked_record = EmissionActivityRecord.objects.select_for_update().get(pk=self.pk)

            if locked_record.is_locked:
                raise ValidationError(
                    "Concurrency Exception: This entry has already been audited and locked by another node handshake.")

            self.approval_status = 'APPROVED'
            self.is_locked = True
            self.approved_by = user
            self.approved_at = timezone.now()
            self.save()