# python modules
import unittest
import os
from datetime import datetime

from bs4 import BeautifulSoup

# package modules
from scrapers.bicycle_warehouse import BicycleWarehouse

#######################################
#  MODULE CONSTANTS
#######################################
TIMESTAMP = datetime.now().strftime('%m%d%Y')
MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'data'))
TEST_DATA_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_data'))
HTML_PATH = os.path.abspath(os.path.join(MODULE_DIR, 'test_html'))
SHOP_BIKES_HTML_PATH = os.path.abspath(os.path.join(HTML_PATH,
                                                    'bicycle-warehouse.html'))
SHOP_ROAD_HTML_PATH = os.path.abspath(os.path.join(
    HTML_PATH, 'bicycle-warehouse-roadbikes.html'))
SHOP_ROAD_FROM_HTML_PATH = os.path.abspath(os.path.join(
    HTML_PATH, 'bicycle-warehouse-roadbikes-from.html'))
SHOP_NO_NEXT_HTML_PATH = os.path.abspath(os.path.join(
    HTML_PATH, 'bicycle-warehouse-no-next.html'))
SAMPLE_SPECS1 = {'frame': 'Reynolds 631 Chromoly Custom Butted, Tapered Headtube, 142x12mm Thru Axles, Disc Tabs', 'fork': 'Carbon/Alloy Tapered Steer, Post Mount Disc, 15mm Thru Axles', 'headset': 'Integrated Cartridge Bearings', 'cranks': 'Praxis Works Alba M30, 38 Tooth Direct Mount', 'bottom_bracket': 'Praxis Works M30 External Bearings', 'rear_derailleur': 'SRAM Rival 1, 11 Speed', 'shifter': 'SRAM Rival 1 HRD, 11 Speed', 'cogset_cassette_freewheel': 'SRAM PG1130, 11 Speed, 11-42', 'chain': 'KMC X11EL-1', 'front_hub': 'Alloy Disc, Cartridge Bearing, 15mm Thru Axle, 28 Hole', 'rear_hub': 'Alloy Disc, Cartridge Bearing, Thru Axle, 28 Hole', 'spokes': '14/15g Butted Stainless with Brass Nipples', 'rims': 'HED Tomcat Disc, 28 Hole, Tubless Compatible', 'tires': "Clement X'PLOR MSO, 700x40c, 60TPI, Folding", 'brakes': 'SRAM Rival Hydraulic Disc, 160mm Rotors', 'brake_levers': 'SRAM Rival', 'pedals': 'Resin Platform Pedal', 'handlebar': 'HED Eroica, 31.8 with 16 Degree Flare, 38/40/42/44/46', 'stem': 'HED Eroica, 31.8, Lengths:/90/100/110/mm', 'seat': 'WTB Volt Race', 'seatpost': 'HED Eroica, 27.2', 'extras': 'Tubeless Valves, Rack and Fender Mounts, third bottle cage mount, Travel Bag'}
SAMPLE_SPECS2 = {'sizes': 'XS, S, M, M/L, L, XL', 'colors': 'Neon Red / Black Chrome, Matte Black / Gloss Black', 'frame': 'ALUXX SL-Grade Aluminum', 'fork': 'Advanced-Grade Composite, alloy OverDrive steerer', 'shock': 'N/A', 'handlebar': 'Giant Connect flat', 'stem': 'Giant Connect, 8-degree', 'seatpost': 'Giant D-Fuse, composite', 'saddle': 'Giant Contact (neutral)', 'pedals': 'Platform', 'shifters': 'Shimano Tiagra, 2x10', 'front_derailleur': 'Shimano Tiagra', 'rear_derailleur': 'Shimano Tiagra', 'brakes': 'TRP flat mount HD-R210 {F] 140mm rotor [R] 140mm rotor, custom caliper', 'brake_levers': 'TRP HD-R210', 'cassette': 'CS-HG500, 11x34', 'chain': 'KMC X10 with Missing Link', 'crankset': 'FC-RS400, 34/50', 'bottom_bracket': 'Shimano, threaded', 'rims': 'Giant S-R2 disc, tubeless wheelset', 'hubs': 'Giant S-R2 disc, tubeless wheelset', 'spokes': 'Giant S-R2 disc, tubeless wheelset', 'tires': 'Gavia AC 2 tubeless, 700x28', 'extras': 'Contact Ergo Max bar end'}
SAMPLE_SPECS3 = {'sizes': 'XS, S, M, L, XL', 'colors': 'Metallic Black / Metallic Orange, Glacier Green/ Pure Red / Navy Blue', 'frame': 'ALUXX SL-Grade Aluminum', 'fork': 'Suntour AION 35-Boost RC DS 27.5+, 150mm travel, Boost QR15x110mm, tapered steerer', 'shock': 'RockShox Deluxe R, trunnion mount', 'handlebar': 'Giant Connect Trail, 780x31.8mm', 'stem': 'Giant Connect', 'seatpost': 'Giant Contact Switch dropper post with remote lever, 30.9mm', 'saddle': 'Giant Contact (neutral)', 'pedals': 'N/A', 'shifters': 'Shimano Deore, 1x10', 'front_derailleur': 'N/A', 'rear_derailleur': 'Shimano Deore , Shadow+', 'brakes': 'Shimano BR-MT400 [F] 180mm [R] 180mm, hydraulic disc', 'brake_levers': 'Shimano BL-MT400', 'cassette': 'Shimano Deore CS-HG500-10, 11x42', 'chain': 'KMC X10-1', 'crankset': 'Praxis Cadet, Boost, 30', 'bottom_bracket': 'Praxis BB-90 Press Fit', 'rims': 'Giant AM 27.5, tubeless ready, sleeve-joint rim, 30mm inner width', 'hubs': '[F] Giant Tracker Performance Boost 15x110mm, sealed bearing [R] Giant Tracker Performance, Boost 12x148, sealed bearing', 'spokes': 'Sapim', 'tires': '[F] Maxxis high Roller II 27.5x2.5 WT, 60 tpi, EXO, TR [R] Maxxis high Roller II 27.5x2.4, 60 tpi, EXO, TR, tubeless'}
SAMPLE_SPECS4 = {'available_frame_sizes': 'S, M, L', 'available_colors': 'SANTA FE SAND; MILLITARY GREEN / CEMENT GREY', 'frame': 'NINER RDO CARBON FIBER, 140MM TRAVEL, GEO FLIP CHIP, RIB CAGE CONSTRUCTION, FULL SLEEVE CABLE ROUTING, ENDURO MAX BLACK OXIDE PIVOT BEARINGS', 'fork': 'FOX 36 FLOAT RHYTHM GRIP EVOL, SWEEP ADJUST, 150MM, 110X15MM, 44MM OFFSET', 'shock': 'FOX FLOAT DPX2 PERFORMANCE EVOL 3 POSITION', 'tubes_sealant': 'STANS NO TUBES SEALANT (2 X 2OZ BOTTLES)', 'front_wheel': 'NINER ALLOY, 110X15MM FRONT, NINER GRAPHIC', 'rear_wheel': 'NINER ALLOY, 148X12MM REAR, NINER GRAPHIC', 'front_tire': 'MAXXIS MINION DHF 3C/EXO/TR 2.5 WT FRONT', 'rear_tire': 'MAXXIS AGGRESSOR 2C/EXO/TR 2.5 WT REAR', 'brakes': 'SRAM LEVEL', 'brake_levers': 'SRAM LEVEL', 'brake_rotors': '180/180MM G2CS ROTORS', 'chain': 'SRAM NX EAGLE 12SP', 'front_shifter': 'N/A', 'rear_shifter': 'SRAM NX EAGLE 12SP', 'front_derailleur': 'N/A', 'rear_derailleur': 'SRAM PG 1230 11-50T', 'cassette': 'SRAM NX EAGLE 12SP', 'crankset': 'SRAM NX EAGLE DUB 32T', 'bottom_bracket': 'SRAM DUB BSA THREADED', 'saddle': 'NINER CUSTOM TR WITH CR-MO RAILS, PRINTED NINER GRAPHIC', 'seatpost': 'SDG TELLIS (S-125MM, M-150MM, L/XL-170MM)', 'handlebar': 'RACE FACE AEFFECT R 780MM WIDE, 20MM RISE, 35MM CLAMP', 'stem': 'RACE FACE AEFFECT R 40MM, 35MM CLAMP', 'headset': 'NINER INTERNAL ZS SHIS DESCRIPTION ZS44/28.6|ZS56/40', 'grips': 'NINER GRRRIPS L/O NYLON FLANGED'}
SAMPLE_SPECS5 = {'frame': 'Lightweight Aluminum Alloy, w/ Custom Formed Stability Tuned Downtube', 'fork': 'Alloy, Oversized blades, Disc Brake Specific', 'headset': 'Integrated, Sealed Bearing', 'cranks': 'FForged Alloy for TranzX System', 'sprocket': 'Formed Spider, 38tooth w/ chainguard', 'rear_derailleur': 'Shimano Altus', 'shifter': 'Shimano TX50 Thumb Shifter w/ Optical Display', 'cogset_causette_freewheel': 'Shimano 12-32', 'chain': 'KMC X8', 'front_hub': 'Front Hub', 'rear_hub': 'VP Modus, Sealed Bearing, W/ QR', 'spokes': 'Stainless', 'rims': 'XM26, Alloy Double Wall', 'tires': 'Kenda Smooth Rolling City 26x1.95"', 'brakes': 'Tektro Mechanical Disc', 'brake_levers': 'Tektro Ergo 4 finger', 'pedals': 'Resin Body Urban, Sealed Bearing', 'handlebar': 'IZIP Aluminum Alloy', 'grips': 'IZIP Ergo Comfort Control', 'stem': 'IZIP Aluminum Alloy, 3d forged', 'seat': 'IZIP Custom Ergo Performance', 'seatpost': 'IZIP Aluminum Alloy, forged head', 'extras': 'Kickstand, Massload TA42', 'motor': 'TranzX M16 Center Mount, 350W', 'battery': '417Wh DT Mounted', 'display': 'TranzX info screen', 'max_assisted_speed': '20mph', 'range_estimated': '16mi/26km to 35mi/56km'}
SAMPLE_SPECS6 = {'sizes': 'XS, S, M, M/L, L, XL', 'colors': 'Gun Metal Black / Charcoal / Chrome', 'frame': 'Advanced-Grade Composite, disc', 'fork': 'Advanced-Grade Composite, hybrid OverDrive steerer, disc', 'shock': 'N/A', 'handlebar': 'Giant Contact SL Aero', 'stem': 'Giant Contact SL Aero', 'seatpost': 'Giant Vector composite', 'saddle': 'Giant Contact (forward)', 'pedals': 'N/A', 'shifters': 'Shimano Ultegra', 'front_derailleur': 'Shimano Ultegra', 'rear_derailleur': 'Shimano Ultegra', 'brakes': 'Shimano Ultegra, hydraulic', 'brake_levers': 'Shimano Ultegra, hydraulic', 'cassette': 'Shimano Ultegra,11x30', 'chain': 'KMC X11EL-1', 'crankset': 'Shimano Ultegra, 36/52', 'bottom_bracket': 'Shimano Press Fit', 'rims': 'Giant SLR-1 Aero Disc WheelSystem (F:42mm, R:65mm)', 'hubs': 'Giant SLR-1 Aero Disc WheelSystem, 12mm thru-axle, CenterLock', 'spokes': 'Giant SLR-1 Aero Disc WheelSystem', 'tires': 'Giant Gavia AC 1 tubeless, 700x25, folding'}
SAMPLE_SPECS7 = {'frame': 'Full CrMo, Integrated Headtube, w/6mm Dropouts, 20.8" TT, Mid BB, Removable Brake Posts & Cable Stop, Integrated Seat Clamp w/Head tube/BB & Dropout Heat Treated', 'fork': 'Free Agent Full CrMo Heat Treated Tapered Leg w/ Free Agent Threaded CNC Free Agent Top Cap', 'headset': 'Free Impact S/B Integrated, Threadless 1-1/8 w/Free Agent Threaded CNC Alloy Top Cap', 'handlebar': 'Free Agent Design CrMo, 9" x 740mm w/Tapered X-Bar', 'stem': 'Free Agent Alloy Top Load', 'grips': 'Free Agent Kraton', 'crankset': 'Free Agent Mid 3-pc Hollow CrMo, 175mm, Free Agent 25T Chainwheel', 'bb': 'Mid Cartridge Bearings, 8 Spline', 'chain': 'KMC Z410', 'pedals': 'Free Agent Low Profile Platform, Smoke', 'rims': 'Free Agent Alloy 20", Double Wall Rear, 36x36H', 'hubset': 'Free Agent Alloy FT 3/8", Alloy RR w/9T Driver, 14mm Axle', 'spokes': '14G Black, 36x36', 'tires': 'Maxxis Grifter, 120 TPI, 110 psi, 20x2.3 FT & RR, Folding Silkshield', 'freewheel_cassette': '9T Driver', 'brake_levers': 'Tektro Alloy 2F w/Hinged Bracket, XL-510', 'brakes_r': 'ProMax U910R, U-Brake w/Green Pads', 'saddle': 'Free Agent, Padded Pivotal', 'seatposts': 'Free Agent Nylon Pivotal', 'other_features': 'Ciclovation Long Linear Cable, Removable HT Cable Guide', 'color': 'Red'}
SAMPLE_SPECS8 = {'frame': '100% Chromoly - Butted TT & DT', 'top_tube': '21"', 'chain_stay': '13.5"', 'head_tube': '75*', 'seat_tube': '71*', 'stand_over': '9.0"', 'brake_mounts': 'Removable', 'fork': '100% Chromoly 1pc ST - 30mm Offset', 'bars': '100% Chromoly - 2pc 9.0"', 'grips': 'Shadow Chula DCR', 'bar_ends': 'Shadow Nylon', 'headset': 'Bang Ur Headset Integrated', 'stem': 'Shadow Chula Top Load', 'front_rim': 'RANT Squad 36H Alloy Double Wall', 'rear_rim': 'RANT Squad 36H Alloy Double Wall', 'front_hub': 'RANT Party On Sealed Female', 'rear_hub': 'RANT Party On Sealed Cassette Male', 'tires': 'Shadow Valor 2.40" LP', 'cranks': 'Shadow Killer Cranks 3pc 175mm', 'bottom_bracket': 'Sealed Mid', 'sprocket': 'Shadow Kobra', 'gearing': '28 - 9', 'chain': 'Shadow Interlock V2', 'pedals': 'Shadow Ravager Plastic', 'seat': 'Signature Shadow Penumbra', 'seat_clamp': 'Shadow Alfred', 'brake_lever': 'RANT Spring Brake Hinged Lever', 'brakes': 'RANT Spring Brakes', 'extras': 'Subrosa Power Pegs x2, RANT Hub Guards x2'}
SAMPLE_SPECS9 = {'frame': '100% 1020 High-Ten Steel', 'top_tube': '20.0"', 'chain_stay': '13.25"', 'head_tube': '75*', 'seat_tube': '71*', 'stand_over': '8.0"', 'brake_mounts': 'Welded', 'fork': '100% 1020 Hi-Ten Steel - 30mm Offset', 'bars': '100% 1020 Hi-Ten Steel - 2pc 7.75"', 'grips': 'Shadow Ol Dirty DCR', 'bar_ends': 'Shadow Nylon', 'headset': '1 1/8" Threadless', 'stem': 'Rant Jolt Top Load', 'front_rim': 'RANT Squad 36H Alloy Single Wall', 'rear_rim': 'RANT Squad 36H Alloy Single Wall', 'front_hub': '3/8" Loose Alloy', 'rear_hub': '14mm Sealed Cassette', 'tires': 'Rant Squad 2.35"', 'cranks': 'Chromoly 3pc 8 Spline 170mm', 'bottom_bracket': 'American Loose Ball', 'sprocket': 'Subrosa Shred Steel', 'gearing': '25 - 9', 'chain': 'RANT Max 410', 'pedals': 'RANT Shred Plastic', 'seat': 'Subrosa Static Mid 1pc Combo', 'seat_clamp': 'Shadow Alfred', 'brake_lever': 'Alloy 2 Finger', 'brakes': 'RANT Spring Brakes'}
SAMPLE_SPECS10 = {'frame': "Women's Specific AL-6061 Double Butted Alloy Disc Frame with Thru-Axles", 'fork': 'Custom Carbon to Alloy 1-1/8" to 1.5 taper, Thru-Axle with Post Disc Mounts', 'cranks': 'Forged 2PC Compact 34/50t', 'bottom_bracket': 'External Bearing', 'front_derailleur': 'Shimano 105', 'rear_derailleur': 'Shimano 105', 'shifter': 'Shimano 105 11spd STI, Shimano SP41 Shift Housing', 'brake_levers': 'Shimano 105 STI', 'brakes': 'TRP Spyre C dual actuated mechanical disc brakes, w/160mm rotors', 'cogset': 'Shimano 11spd (11-32t)', 'rims': 'Weinmann XC180 Double Wall 23mm Wide', 'tires': 'Clement Strada LGG 60TPI, 700x28c', 'pedals': 'Test Ride Pedals', 'handlebar': 'Raleigh 200 Series Aero Ergo Flat Top Road, 31.8 with 6 Degree Flare, 38/40/42cm', 'stem': '3D Forged Anti-Shock, 31.8, 80/90/100mm', 'seatpost': 'Anti-Shock 27.2x300mm', 'seat': 'Raleigh 200 series Saddle', 'headset': 'Integrated Cartridge Bearings', 'chain': 'KMC X11', 'front_hub': 'Formula Alloy Disc 15mm Thru-Axle', 'rear_hub': 'Formula Alloy Disc 142x12mm Thru-Axle Cassette', 'spokes': '14g Stainless MAC'}


class SpecializedTestCase(unittest.TestCase):
    def setUp(self):
        self._scraper = BicycleWarehouse(save_data_path=DATA_PATH)

    def test_get_categories(self):
        categories = [
            'road_bikes',
            'mountain_bikes',
            'electric_bikes',
            'path_pavement',
            'bmx_bikes'
        ]

        result = self._scraper._get_categories()
        print('\nCategories:', result)
        self.assertEqual(len(categories), len(result),
                         msg=f'Expected {len(categories)}; result {len(result)}')
        for key in categories:
            self.assertTrue(key in result,
                            msg=f'{key} is not in {result}!')

    def test_get_prods_listings(self):
        bike_type = 'road_bikes'
        bike_cats = self._scraper._get_categories()
        endpoint = bike_cats[bike_type]['href']
        soup = BeautifulSoup(self._scraper._fetch_prod_listing_view(
            endpoint), 'lxml')

        # Verify product listings fetch
        self._scraper._get_prods_on_current_listings_page(soup, bike_type)
        num_prods = len(self._scraper._products)
        self.assertTrue(num_prods > 5,
                        msg=f'There are {num_prods} product first page.')
        self._scraper._write_prod_listings_to_csv()

    def test_parse_specs(self):
        bike_type = 'road_bikes'
        prods_csv_path = os.path.join(DATA_PATH, TIMESTAMP,
                                      'bicycle_warehouse_prods_all.csv')
        # Verify parsing product specs
        specs = self._scraper.get_product_specs(get_prods_from=prods_csv_path,
                                                bike_type=bike_type,
                                                to_csv=False)
        num_prods = len(self._scraper._products)
        num_specs = len(specs)
        self.assertEqual(num_prods, num_specs,
                         msg=f'Products size: {num_prods}, Specs size: {num_specs}')
        self._scraper._write_prod_specs_to_csv(specs=specs,
                                               bike_type=bike_type)

        # Verify spec fieldnames has minimum general fields:
        expected = ['site', 'product_id', 'frame',
                    'fork', 'cassette', 'saddle', 'seatpost']
        print('\nSpec Fieldnames\n', self._scraper._specs_fieldnames)
        for field in expected:
            self.assertTrue(field in self._scraper._specs_fieldnames,
                            msg=f'{field} not in {self._scraper._specs_fieldnames}.')

    def test_get_all_available_prods(self):
        expected = 24 * 5
        # Validate method
        self._scraper.get_all_available_prods()
        num_prods = len(self._scraper._products)
        # There are dupes so expect less num_prods
        self.assertTrue(num_prods > expected,
                        msg=f'expected: {expected} - found: {num_prods}')


if __name__ == '__main__':
    unittest.main()
