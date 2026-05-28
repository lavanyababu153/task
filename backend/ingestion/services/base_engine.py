
from abc import ABC, abstractmethod
from django.db import transaction
from emissions.models import IngestionJobLog, EmissionActivityRecord


class BaseIngestionEngine(ABC):
    def __init__(self, organization):
        self.organization = organization

    @abstractmethod
    def source_type(self) -> str:
        """Returns 'SAP', 'UTILITY', or 'TRAVEL'"""
        pass

    @abstractmethod
    def parse_and_validate(self, raw_data) -> list:
        """
        Parses raw data into an un-saved list of dictionaries.
        Calculates carbon footprints and catches data shape flags.
        """
        pass

    def process_ingestion(self, raw_payload_str: str, filename=None):
        """
        Executes the ingestion pipeline inside an atomic transaction.
        Guarantees that partial data corruptions roll back completely.
        """
        with transaction.atomic():
            # 1. Create a Master Lineage Log Tracker
            job_log = IngestionJobLog.objects.create(
                organization=self.organization,
                source_type=self.source_type(),
                filename=filename,
                raw_payload_backup=raw_payload_str
            )


            parsed_rows = self.parse_and_validate(raw_payload_str)

            records_to_create = []
            for row in parsed_rows:
                record = EmissionActivityRecord(
                    organization=self.organization,
                    job_source=job_log,
                    scope_category=row['scope_category'],
                    ghg_mapping_category=row['ghg_mapping_category'],
                    original_quantity=row['original_quantity'],
                    original_unit=row['original_unit'],
                    normalized_quantity_co2e=row['normalized_quantity_co2e'],
                    activity_start_date=row['activity_start_date'],
                    activity_end_date=row['activity_end_date'],
                    validation_status=row['validation_status'],
                    validation_notes=row.get('validation_notes', '')
                )
                records_to_create.append(record)


            EmissionActivityRecord.objects.bulk_create(records_to_create)
            return job_log