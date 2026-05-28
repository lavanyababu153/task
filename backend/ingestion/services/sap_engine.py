
import csv
import io
from datetime import datetime
from decimal import Decimal
from .base_engine import BaseIngestionEngine


class SAPIngestionEngine(BaseIngestionEngine):
    def source_type(self) -> str:
        return 'SAP'

    def parse_and_validate(self, raw_data_str: str) -> list:
        parsed_results = []

        f = io.StringIO(raw_data_str.strip())
        reader = csv.DictReader(f)

        EMISSION_FACTORS = {
            '400120': Decimal('0.00268'),
            '100450': Decimal('0.00015'),
        }

        for row in reader:

            mat_nr = row.get('MATNR', '').strip()
            raw_qty = row.get('MENGE', '0')
            unit = row.get('MEINS', '').strip()
            sap_date_str = row.get('BUDAT', '')  #

            try:
                quantity = Decimal(raw_qty)
                parsed_date = datetime.strptime(sap_date_str, '%Y%m%d').date()


                status = 'VALID'
                notes = ''


                if quantity > 50000:
                    status = 'SUSPICIOUS'
                    notes = "Automated Flag: Exceptionally high quantity detected for a single SAP booking reference line."

                factor = EMISSION_FACTORS.get(mat_nr, Decimal('0.00005'))
                co2e = quantity * factor

                parsed_results.append({
                    'scope_category': 'SCOPE_1' if mat_nr == '400120' else 'SCOPE_3',
                    'ghg_mapping_category': f"SAP Material Code {mat_nr}",
                    'original_quantity': quantity,
                    'original_unit': unit,
                    'normalized_quantity_co2e': co2e,
                    'activity_start_date': parsed_date,
                    'activity_end_date': parsed_date,
                    'validation_status': status,
                    'validation_notes': notes
                })
            except Exception as e:

                parsed_results.append({
                    'scope_category': 'SCOPE_1',
                    'ghg_mapping_category': "Unparseable SAP Reference Data Line",
                    'original_quantity': Decimal('0.00'),
                    'original_unit': unit or 'UNKNOWN',
                    'normalized_quantity_co2e': Decimal('0.00'),
                    'activity_start_date': datetime.now().date(),
                    'activity_end_date': datetime.now().date(),
                    'validation_status': 'FAILED',
                    'validation_notes': f"Parsing failure rule break: {str(e)}"
                })
        return parsed_results