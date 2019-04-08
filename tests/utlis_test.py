import unittest

from scrapers.scraper_utils import get_bike_type_from_desc


class UtilsTestCase(unittest.TestCase):
    def setup(self):
        pass

    def test_get_bike_type_from_desc(self):
        """Test case for determining bike type from description."""
        test_cases = {
            'kid': [
                'SE Bikes Micro Ripper 12" Kids Bike - 2019',
                'Fuji Ace 650 Kid\'s Road Bike'
            ],
            'girl': [
                'Phat Cycles Melodie 24" Girl\'s Beach Cruiser',
                'Phat Cycles Melodie 24" Girls Beach Cruiser'
            ],
            'frame': [
                'Fuji Roubaix Elite Road Frameset - 2018',
                'Nashbar Carbon Cyclocross Frame and Fork',
                'SE Showtime 26" BMX/Fixed Gear Frame - Closeout',
                'Breezer Radar Pro Gravel Frameset - 2018'
            ],
            'fork': [
                '3T Funda Pro Road Fork',
                'Nashbar Carbon Cyclocross Fork',
                'Nashbar Chromoly 29" Mountain Fork'
            ],
            'bmx': [
                'SE STR-24 Quadangle 24" BMX Bike - 2019',
                'SE Fat Ripper 26" BMX Bike - 2019'
            ],
            'road': [
                'SE Monterey 1.0 Women\'s Flatbar Road Bike',
                'Cavalo 105 Alloy Road Bike'
            ],
            'mountain': [
                'Fuji Rakan 3.4 29er Full Suspension Mountain Bike -- 2018',
                'Nashbar Women\'s 26" Disc Mountain Bike'
            ],
            'cyclocross': [
                'Nashbar Single-Speed Cyclocross Bike',
                'Fuji Altamira CX 1.3 Cyclocross Bike - 2018'
            ],
            'hybrid': [
                'Fuji Traverse 1.5 Disc Women\'s Sport Hybrid - 2017',
                'Nashbar Dual Sport Hybrid Bike'
            ],
            'gravel': [
                'Breezer Radar Expert Gravel Bike - 2018',
                'Fuji Jari 2.5 Gravel Bike - 2018'
            ],
            'city': [
                'Fuji League City Bike - 2018',
                'Raleigh Teaba Single-Speed City Bike - Closeout'
            ],
            'commuter': [
                'Breezer Uptown 8 Women\'s Commuter Bike',
                'Cavalo Derailleur Commuter Hanger 20'
            ],
            'comfort': [
                'Breezer Greenway Elite ST Comfort Bike - 2015',
                'Marin Stinson Comfort Bike'
            ],
            'cruiser': [
                'Fuji Cape May ST Women\'s Beach Cruiser',
                'Tuesday June 7 24" Cruiser'
            ],
            'e-bike': [
                'Tuesday August Live! Cruiser e-Bike - 2019',
                'Tuesday August Live! Cruiser Low-Step e-Bike - 2019'
            ],
            'fat': [
                'Fuji Wendigo 26 1.1 Fat Bike - 2017',
                'SE F@R 26 Fat Bike - 2017'
            ],
            'triathlon': [
                'Fuji Norcom Straight 2.5 Triathlon Bike - 2015',
                'Kestrel 5000 SL Shimano Ultegra Triathlon/Time Trial Bike - 2018'
            ],
            None: [
                'Nashbar Derailleur Hanger 2',
                'Park Tool CG-2.3 Chain Gang Chain Cleaning System',
                'Oregon Bike Tax - $15'
            ]
        }
        for bike_type in test_cases.keys():
            for desc in test_cases[bike_type]:
                result = get_bike_type_from_desc(desc)
                self.assertEqual(result, bike_type,
                                 msg=f'Failed to match "{desc}"')


if __name__ == '__main__':
    unittest.main()
