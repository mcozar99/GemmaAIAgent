import csv
import os

# Place the CSV where the application expects it (project_root/src/loads.csv)
BASE_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(BASE_DIR)
CSV_PATH = os.path.join(PROJECT_ROOT, 'src', 'loads.csv')


def init_csv():
    headers = [
        'load_id',
        'origin',
        'destination',
        'pickup_datetime',
        'delivery_datetime',
        'equipment_type',
        'loadboard_rate',
        'notes',
        'weight',
        'commodity_type',
        'num_of_pieces',
        'miles',
        'dimensions',
    ]

    sample_rows = [
        {
            'load_id': 'L001',
            'origin': 'Los Angeles, CA',
            'destination': 'Las Vegas, NV',
            'pickup_datetime': '2025-10-10 08:00',
            'delivery_datetime': '2025-10-10 14:00',
            'equipment_type': 'Reefer',
            'loadboard_rate': '1500',
            'notes': 'Handle with care',
            'weight': '12000',
            'commodity_type': 'Produce',
            'num_of_pieces': '100',
            'miles': '270',
            'dimensions': '48x40x96',
        },
        {
            'load_id': 'L002',
            'origin': 'Chicago, IL',
            'destination': 'Detroit, MI',
            'pickup_datetime': '2025-10-12 09:30',
            'delivery_datetime': '2025-10-12 13:00',
            'equipment_type': 'Dry Van',
            'loadboard_rate': '800',
            'notes': '',
            'weight': '8000',
            'commodity_type': 'Electronics',
            'num_of_pieces': '50',
            'miles': '283',
            'dimensions': '48x40x60',
        },
        {
            'load_id': 'L003',
            'origin': 'Houston, TX',
            'destination': 'Atlanta, GA',
            'pickup_datetime': '2025-10-15 07:00',
            'delivery_datetime': '2025-10-16 18:00',
            'equipment_type': 'Flatbed',
            'loadboard_rate': '2200',
            'notes': 'Oversize - permit required',
            'weight': '20000',
            'commodity_type': 'Steel',
            'num_of_pieces': '10',
            'miles': '800',
            'dimensions': '240x96x60',
        },
        {
            'load_id': 'L004',
            'origin': 'Seattle, WA',
            'destination': 'Portland, OR',
            'pickup_datetime': '2025-10-20 10:00',
            'delivery_datetime': '2025-10-20 15:00',
            'equipment_type': 'Dry Van',
            'loadboard_rate': '600',
            'notes': 'Short haul',
            'weight': '5000',
            'commodity_type': 'Furniture',
            'num_of_pieces': '8',
            'miles': '174',
            'dimensions': '60x48x72',
        },
        {
            'load_id': 'L005',
            'origin': 'Miami, FL',
            'destination': 'Orlando, FL',
            'pickup_datetime': '2025-10-18 06:00',
            'delivery_datetime': '2025-10-18 11:00',
            'equipment_type': 'Reefer',
            'loadboard_rate': '400',
            'notes': 'Temperature controlled',
            'weight': '6000',
            'commodity_type': 'Pharmaceuticals',
            'num_of_pieces': '20',
            'miles': '230',
            'dimensions': '48x40x60',
        },
        {
            'load_id': 'L006',
            'origin': 'Newark, NJ',
            'destination': 'Boston, MA',
            'pickup_datetime': '2025-10-22 12:00',
            'delivery_datetime': '2025-10-22 18:00',
            'equipment_type': 'Dry Van',
            'loadboard_rate': '950',
            'notes': '',
            'weight': '10000',
            'commodity_type': 'Retail Goods',
            'num_of_pieces': '200',
            'miles': '220',
            'dimensions': '48x40x72',
        },
        {
            'load_id': 'L007',
            'origin': 'Phoenix, AZ',
            'destination': 'Denver, CO',
            'pickup_datetime': '2025-10-25 05:30',
            'delivery_datetime': '2025-10-25 18:00',
            'equipment_type': 'Flatbed',
            'loadboard_rate': '1800',
            'notes': 'Load with tie-downs',
            'weight': '15000',
            'commodity_type': 'Machinery',
            'num_of_pieces': '3',
            'miles': '825',
            'dimensions': '120x80x80',
        },
        {
            'load_id': 'L008',
            'origin': 'San Francisco, CA',
            'destination': 'Sacramento, CA',
            'pickup_datetime': '2025-10-30 09:00',
            'delivery_datetime': '2025-10-30 12:00',
            'equipment_type': 'Dry Van',
            'loadboard_rate': '350',
            'notes': '',
            'weight': '4000',
            'commodity_type': 'Clothing',
            'num_of_pieces': '500',
            'miles': '87',
            'dimensions': '48x40x60',
        },
        {
            'load_id': 'L009',
            'origin': 'Cleveland, OH',
            'destination': 'Columbus, OH',
            'pickup_datetime': '2025-11-01 07:00',
            'delivery_datetime': '2025-11-01 10:00',
            'equipment_type': 'Dry Van',
            'loadboard_rate': '275',
            'notes': 'Local delivery',
            'weight': '3000',
            'commodity_type': 'Parts',
            'num_of_pieces': '120',
            'miles': '140',
            'dimensions': '48x40x48',
        },
        {
            'load_id': 'L010',
            'origin': 'Minneapolis, MN',
            'destination': 'St. Paul, MN',
            'pickup_datetime': '2025-11-03 08:00',
            'delivery_datetime': '2025-11-03 09:30',
            'equipment_type': 'Dry Van',
            'loadboard_rate': '200',
            'notes': 'Quick hop',
            'weight': '2500',
            'commodity_type': 'Food',
            'num_of_pieces': '60',
            'miles': '15',
            'dimensions': '48x40x48',
        },
    ]

    # Write header and sample rows
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in sample_rows:
            writer.writerow(row)

    print(f'CSV initialized at: {CSV_PATH} with {len(sample_rows)} sample rows')


if __name__ == '__main__':
    init_csv()

