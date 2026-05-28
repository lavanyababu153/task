import csv
import io
from datetime import datetime
from decimal import Decimal
from .base_engine import BaseIngestionEngine


class UtilityIngestionEngine(BaseIngestionEngine):
    def source_type(self) -> str:
        return 'UTILITY'

    def parse_and_validate(self, raw_data_str: str) -> list:
        parsed_results = []
        f = io.StringIO(raw_data_str.strip())
        reader = csv.DictReader(f)


        ELEC_FACTOR = Decimal('0.00038')

        for row in reader:

            try:
                start_date = datetime.strptime(row['Bill_Start_Date'].strip(), '%Y-%m-%d').date()
                end_date = datetime.strptime(row['Bill_End_Date'].strip(), '%Y-%m-%d').date()
                kwh = Decimal(row['Usage_kWh'].strip())

                status = 'VALID'
                notes = ''


                if kwh <= 0:
                    status = 'FAILED'
                    notes = "Data Integrity Violation: Meter consumption values must be strictly positive."
                elif (end_date - start_date).days > 35:
                    status = 'SUSPICIOUS'
                    notes = f"Billing cycle anomaly: Period spans {(end_date - start_date).days} days. Exceeds standard monthly frame."

                co2e = kwh * ELEC_FACTOR if status != 'FAILED' else Decimal('0.0000')

                parsed_results.append({
                    'scope_category': 'SCOPE_2',
                    'ghg_mapping_category': f"Purchased Grid Electricity (Meter: {row.get('Meter_ID')})",
                    'original_quantity': kwh,
                    'original_unit': 'kWh',
                    'normalized_quantity_co2e': co2e,
                    'activity_start_date': start_date,
                    'activity_end_date': end_date,
                    'validation_status': status,
                    'validation_notes': notes
                })
            except Exception as e:
                parsed_results.append({
                    'scope_category': 'SCOPE_2',
                    'ghg_mapping_category': "Critical Utility Format Failure",
                    'original_quantity': Decimal('0.00'),
                    'original_unit': 'kWh',
                    'normalized_quantity_co2e': Decimal('0.00'),
                    'activity_start_date': datetime.now().date(),
                    'activity_end_date': datetime.now().date(),
                    'validation_status': 'FAILED',
                    'validation_notes': f"Format Error: {str(e)}"
                })
        return parsed_results