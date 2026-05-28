
import json
from datetime import datetime
from decimal import Decimal
from .base_engine import BaseIngestionEngine


class TravelIngestionEngine(BaseIngestionEngine):
    def source_type(self) -> str:
        return 'TRAVEL'

    def parse_and_validate(self, raw_json_str: str) -> list:
        parsed_results = []


        ROUTE_DISTANCES = {
            'JFK-LHR': Decimal('5540'),
            'SFO-JFK': Decimal('4160'),
            'LHR-CDG': Decimal('350'),
        }


        EMISSION_FACTORS = {
            'ECONOMY': Decimal('0.00015'),
            'BUSINESS': Decimal('0.00043'),
        }

        try:
            payload = json.loads(raw_json_str)
            trips = payload.get('bookings', [])
        except Exception as e:
            return [{
                'scope_category': 'SCOPE_3',
                'ghg_mapping_category': "Corrupted Travel Payload Batch",
                'original_quantity': Decimal('0.00'),
                'original_unit': 'JSON',
                'normalized_quantity_co2e': Decimal('0.00'),
                'activity_start_date': datetime.now().date(),
                'activity_end_date': datetime.now().date(),
                'validation_status': 'FAILED',
                'validation_notes': f"JSON Root Level structural breakdown error: {str(e)}"
            }]

        for trip in trips:
            try:
                origin = trip.get('origin_airport', '').strip().upper()
                dest = trip.get('destination_airport', '').strip().upper()
                cabin = trip.get('cabin_class', 'ECONOMY').strip().upper()
                date_str = trip.get('booking_date', '')
                parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()

                route_key = f"{origin}-{dest}"
                reverse_route_key = f"{dest}-{origin}"


                distance = ROUTE_DISTANCES.get(route_key, ROUTE_DISTANCES.get(reverse_route_key, None))

                status = 'VALID'
                notes = ''

                if distance is None:
                    distance = Decimal('1000')
                    status = 'SUSPICIOUS'
                    notes = f"Route Map Missing: Air route distance code fallback activated for path: '{route_key}'."

                factor = EMISSION_FACTORS.get(cabin, Decimal('0.00015'))
                co2e = distance * factor

                parsed_results.append({
                    'scope_category': 'SCOPE_3',
                    'ghg_mapping_category': f"Business Travel: Flight {route_key} ({cabin} Class)",
                    'original_quantity': distance,
                    'original_unit': 'Passenger-Kilometers',
                    'normalized_quantity_co2e': co2e,
                    'activity_start_date': parsed_date,
                    'activity_end_date': parsed_date,
                    'validation_status': status,
                    'validation_notes': notes
                })
            except Exception as e:
                parsed_results.append({
                    'scope_category': 'SCOPE_3',
                    'ghg_mapping_category': "Individual Booking Entry Parsing Failure",
                    'original_quantity': Decimal('0.00'),
                    'original_unit': 'ENTRY_ERR',
                    'normalized_quantity_co2e': Decimal('0.00'),
                    'activity_start_date': datetime.now().date(),
                    'activity_end_date': datetime.now().date(),
                    'validation_status': 'FAILED',
                    'validation_notes': f"Row Parsing Failure: {str(e)}"
                })
        return parsed_results