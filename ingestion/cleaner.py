"""Module for cleaning each product specs csv file into standard format and then
merging with products csv file into standard munged data file for each source."""

import re
import math
import os
import pandas as pd
import numpy as np

# Project modules
from utils.utils import MUNGED_DATA_PATH


class Cleaner(object):
    def __init__(self, mediator, save_data_path=MUNGED_DATA_PATH):
        self._mediator = mediator
        self._save_data_path = save_data_path
        self._FIELD_NAMES = [
            'site', 'bike_type', 'product_id', 'href', 'description',
            'brand', 'price', 'msrp', 'frame_material',
            'model_year', 'brake_type', 'fork_material',
            'handlebar_material', 'fd_groupset',
            'rd_groupset', 'cassette_groupset',
            'crankset_material', 'crankset_groupset',
            'seatpost_material', 'chain_groupset',
            'shifter_groupset'
        ]
        self._GROUPSET_RANKING = {
            'shimano claris': 1,
            'shimano sora': 2,
            'shimano tiagra': 2,
            'shimano 105': 3,
            'shimano ultegra': 4,
            'shimano ultegra di2': 5,
            'shimano dura-ace': 5,
            'shimano dura-ace di2': 6,
            'sram apex': 2,
            'sram rival': 3,
            'sram s700': 3,
            'sram force': 4,
            'sram red': 5,
            'sram red etap': 6,
            'campagnolo veloce': 1,
            'campagnolo centaur': 3,
            'campagnolo athena': 2.5,
            'campagnolo potenza': 4,
            'campagnolo chorus': 4,
            'campagnolo athena eps': 3.5,
            'campagnolo record': 5,
            'campagnolo chorus eps': 5,
            'campagnolo super record': 5.25,
            'campagnolo record eps': 5.5,
            'campagnolo super record eps': 6,
            'shimano tourney': 0.5,
            'shimano altus': 1,
            'shimano acera': 1.5,
            'shimano alivio': 2,
            'shimano deore': 2.75,
            'shimano slx': 3,
            'shimano zee': 3,
            'shimano deore xt': 4,
            'shimano xt': 4,  # ?
            'shimano saint': 4.5,
            'shimano xt di2': 4,
            'shimano xtr': 5,
            'shimano xtr di2': 6,
            'sram x3': 0.5,
            'sram x4': 1.5,
            'sram x5': 2,
            'sram x7': 2.25,
            'sram x9': 2.6,
            'sram nx': 3,
            'sram gx dh': 3,
            'sram gx': 3.25,
            'sram gx eagle': 3.5,
            'sram x1': 3.75,
            'sram xO1 dh': 4.25,
            'sram xO': 4.0,
            'sram xO1': 4.25,
            'sram xx': 4.5,
            'sram xx1': 5,
            'sram xO1 eagle': 4.75,
            'sram xx1 eagle': 6,
            'sram via': 3.5,
            'shimano 7-speed': 0.5,
            'shimano 8-speed': 1,
            'shimano 9-speed': 2,
            'shimano 10-speed': 2.5,
            'sram 8-speed': 0.5,
            'sram 9-speed': 1,
            'sram 10-speed': 2,
        }
        self._GROUPSETS_MAP = {
            'claris': 'shimano claris',
            'sora': 'shimano sora',
            'tiagra': 'shimano tiagra',
            '105': 'shimano 105',
            'ultegra': 'shimano ultegra',
            'ultegra di2': 'shimano ultegra di2',
            'dura-ace': 'shimano dura-ace',
            'dura-ace di2': 'shimano dura-ace di2',
            'apex': 'sram apex',
            'rival': 'sram rival',
            's700': 'sram s700',
            'force': 'sram force',
            'red': 'sram red',
            'red etap': 'sram red etap',
            'veloce': 'campagnolo veloce',
            'centaur': 'campagnolo centaur',
            'athena': 'campagnolo athena',
            'potenza': 'campagnolo potenza',
            'chorus': 'campagnolo chorus',
            'athena eps': 'campagnolo athena eps',
            'record': 'campagnolo record',
            'chorus eps': 'campagnolo chorus eps',
            'super record': 'campagnolo super record',
            'record eps': 'campagnolo record eps',
            'super record eps': 'campagnolo super record eps',
            'tourney': 'shimano tourney',
            'altus': 'shimano altus',
            'acera': 'shimano acera',
            'alivio': 'shimano alivio',
            'deore': 'shimano deore',
            'slx': 'shimano slx',
            'zee': 'shimano zee',
            'deore xt': 'shimano deore xt',
            'xt': 'shimano deore xt',
            'saint': 'shimano saint',
            'xt di2': 'shimano xt di2',
            'xtr': 'shimano xtr',
            'xtr di2': 'shimano xtr di2',
            'x3': 'sram x3',
            'x4': 'sram x4',
            'x5': 'sram x5',
            'x7': 'sram x7',
            'x9': 'sram x9',
            'nx': 'sram nx',
            'gx dh': 'sram gx dh',
            'gx': 'sram gx',
            'gx eagle': 'sram gx eagle',
            'x1': 'sram x1',
            'xO1 dh': 'sram xO1 dh',
            'xO': 'sram xO',
            'xO1': 'sram xO1',
            'xx': 'sram xx',
            'xx1': 'sram xx1',
            'xO1 eagle': 'sram xO1 eagle',
            'xx1 eagle': 'sram xx1 eagle',
            'microshift': 'microshift',
            'shimano 2400': 'shimano claris',
            'shimano acero': 'shimano acera',
            'shimano r7000': 'shimano 105',
            'shimano 9150': 'shimano dura-ace di2',
            'shimano 9100': 'shimano dura-ace',
            'shimano 9070': 'shimano dura-ace di2',
            'shimano 9000': 'shimano dura-ace',
            'shimano r8000': 'shimano ultegra',
            'shimano r8050': 'shimano ultegra di2',
            'shimano 6800': 'shimano ultegra',
            'shimano 6870': 'shimano ultegra di2',
            'shimano 5800': 'shimano 105',
            'shimano 4700': 'shimano tiagra',
            'shimano r3000': 'shimano sora',
            'shimano tx800': 'shimano tourney',
            'shimano t4000': 'shimano alivio',
            'shimano ty510': 'shimano tourney',
            'shimano ty700': 'shimano tourney',
            'shimano fd-ty500': 'shimano tourney',
            'shimano fd-m190': 'shimano tourney',
            'shimano mt400': 'shimano alivio',
            'shimano fd-ty710': 'shimano tourney',
            'shimano tz31': 'shimano tourney',
            'shimano tz-30': 'shimano tourney',
            'shimano tz30': 'shimano tourney',
            'shimano a070': 'shimano tourney',
            'shimano st-ef51': 'shimano tiagra',
            'shimano fd-m191': 'shimano altus',
            'sram etap': 'sram red etap',
            'sram x01 eagle': 'sram xO1 eagle',
            'sram x01': 'sram xO1',
            'sram eagle x01': 'sram xO1 eagle',
            'sram eagle xO1': 'sram xO1 eagle',
            'sram eagle xo1': 'sram xO1 eagle',
            'sram via': 'sram via',
            'shimano tx 8000': 'shimano tourney',
            'shimano tx-8000': 'shimano tourney',
            'shimano tx8000': 'shimano deore',
            'shimano rd-m7000': 'shimano slx',
            'shimano m7000': 'shimano slx',
            'shimano rd-m8000': 'shimano deore xt',
            'shimano m8000': 'shimano deore xt',
            'shimano tz-50': 'shimano tourney',
            'shimano tz50': 'shimano tourney',
            'shimano ty300': 'shimano tourney',
            'shimano ty-300': 'shimano tourney',
            'shimano tx-35': 'shimano tourney',
            'shimano tx35': 'shimano tourney',
            'shimano rd-m2000': 'shimano altus',
            'shimano rdm2000': 'shimano altus',
            'shimano rd m2000': 'shimano altus',
            'shimano ft30': 'shimano tourney',
            'shimano ft 30': 'shimano tourney',
            'shimano ft-30': 'shimano tourney',
            'shimano rd-5800': 'shimano 105',
            'shimano rd 5800': 'shimano 105',
            'X01 Eagle': 'sram xO1 eagle',
            'SEAM X01 Eagle': 'sram xO1 eagle',
            'Sram A1': 'sram apex'
        }
        self._BIKE_TYPE = {  # order matters for fork, frame, kid, girl, and bmx as qualifiers
                'frame', 'fork', 'kid', 'girl', 'e-bike', 'electric', 'folding', 'balance',
                'push', 'trailer', 'boy', 'bmx', 'city', 'commuter', 'comfort', 'fitness',
                'cruiser', 'fat', 'triathlon', 'road', 'touring', 'urban',
                'track', 'adventure', 'mountain', 'cyclocross', 'hybrid',
                'gravel', 'pavement', 'gravel', 'cargo', 'hardtail', 'singlespeed'
            }

    def _fill_missing_bike_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Use description to populate missing bike_types values."""

        def parse_desc(desc):
            # relabel some string literals
            desc = desc.lower()
            desc = desc.replace('moutain', 'mountain')  # fix typo
            desc = desc.replace('racing', 'road')  # map to road
            desc = desc.replace('suspension', 'mountain')  # map to mountain
            desc = desc.replace('commute', 'commuter')
            desc = desc.replace('step-through', 'urban')

            for bike_type in self._BIKE_TYPE:
                if re.search(re.escape(bike_type), desc, re.IGNORECASE):
                    return bike_type

            return desc  # np.NaN

        # Populate null values using description field
        for idx in df[df.bike_type.isnull()].index:
            df.loc[idx, 'bike_type'] = parse_desc(df.description[idx])

        return df

    @staticmethod
    def _parse_model_year(desc: pd.Series) -> pd.Series:
        """Use description to populate missing model_year values."""
        def parse_model_year(d):
            result = re.search(pattern=r'20[0-9]{2}', string=d)
            if result is None:
                return np.NaN
            year = int(result.group(0))
            return year if year < 2021 else np.NaN  # avoid '20.75' in href parsing

        return desc.apply(parse_model_year)

    def _normalize_bike_type_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean up bike_type labels and prepare specified categories for removal.
        """
        def bike_type_replace(elem):
            # Custom cleaning
            if 'giant defy advanced' in elem:
                elem = 'road'

            # First pass through mappings
            bike_mapper = {
                'single_speed_fixed_gear_bikes': 'singlespeed',
                'mountain_bikes': 'mountain',
                'Mountain': 'mountain',
                'Mountain Biking': 'mountain',
                'Recreational Cycling': 'urban',
                'Urban Cycling': 'urban',
                'Road Cycling': 'road',
                'Cycling': 'road',
                'road_bikes': 'road',
                'path_pavement_bikes': 'urban',
                'urban_bikes': 'urban',
                'boy': 'childrens',
                'kid': 'childrens',
                'youth': 'childrens',
                'childrens': 'childrens',
                'bmx_bikes': 'bmx',
                'commuter_urban': 'urban',
                'electric': 'ebike',
                'electric_bikes': 'ebike',
                'e-bike': 'ebike',
                'girl': 'childrens',
                'gravel': 'cyclocross',
                'fat': 'mountain',
                'frame': np.NaN,  # prep for dropping since not a complete bike
                'fork': np.NaN,  # prep for dropping since not a complete bike
                'Bike Touring': 'touring',
                'Bike Commuting': 'urban',
                'Road Cycling, Bikepacking': 'touring',
                'Fitness': 'commuter',
                'fitness': 'commuter',
                'pavement': 'commuter',
                'hardtail': 'mountain',
                'balance': 'childrens',
                'push': 'childrens',
                'cargo': 'cargo',
                'trailer': np.NaN,  # prep for dropping since accessory
                'Bikepacking, Bike Touring': 'touring',
                'Mountain Biking, Bikepacking': 'touring',
                'Bikepacking, Mountain Biking': 'touring',
                'Cyclocross': 'cyclocross',
                'Bikepacking, Road Cycling': 'touring',
                'Bike Touring, Bikepacking': 'touring',
                'cruiser': 'comfort',
                'city': 'urban',
                'adventure': 'comfort',
                'triathlon': 'triathlon',
                'track': 'track',
                'cyclocross_gravel_bikes': 'cyclocross',
                'commuter_urban_bikes': 'commuter',
                'kids_bikes': 'childrens',
                'Kids': 'childrens',
                'Trail, All-Mountain, Enduro': 'mountain',
                'Trail, All-mountain, Enduro': 'mountain',
                'Trail, All-mountain': 'mountain',
                'Commuting, Urban, Bike-Path': 'urban',
                'XC': 'mountain', 'All-mountain, Enduro': 'mountain',
                'Trail, All-Mountain': 'mountain',
                'All-Mountain, Recreational, Adventure': 'mountain',
                'XC, Endurance': 'mountain', 'Trail, AM': 'mountain',
                'All-mountain, Enduro, Gravity': 'mountain',
                'Trail': 'mountain', 'Enduro, Mini-DH': 'mountain',
                'XC, Trail': 'mountain', 'Cyclocross, Gravel': 'cyclocross',
                'Race, Sport, Cyclocross, Gravel, Triathlon, Touring, Adventure, Recreational, Urban Commuter':
                'urban', 'Road, Path, Commuting': 'commuter',
                'Road': 'road', 'Road, Racing': 'road',
                'Gravel, Cyclocross': 'cyclocross',
                'Pavement, Paths, Light Trails': 'commuter',
                'Urban, Commuter': 'urban',
                "Cruisin'": 'cruiser', 'Race': 'road',
                'Cruising to the beach or store': 'cruiser',
                'Childrens': 'childrens',
                'Mountain biking, Town riding': 'mountain'
            }
            bike_type = bike_mapper.get(elem, elem)

            # Then second pass for standardization or those missed
            for bike in self._BIKE_TYPE:
                if re.search(re.escape(bike), elem, re.IGNORECASE):
                    bike_type = bike

            return bike_type

        # Clean bike_type labels and drop specified categories
        df.bike_type = df.bike_type.apply(bike_type_replace)
        df = df.drop(df[df.bike_type.isnull()].index)
        df.bike_type.value_counts()

        return df

    @staticmethod
    def _normalize_brands(df: pd.DataFrame) -> pd.DataFrame:
        """Clean up and standardize brand names."""

        def brand_replace(brand):
            brand = brand.replace(' Bikes', '')
            brand = brand.replace(' Bike', '')
            brand = brand.replace(' Bicycles', '')
            brand = brand.replace(' Electric', '')
            brand = brand.replace(' S-Works', '')
            brand = brand.replace(' Cycles', '')
            brand = brand.replace(' Turbo', '')
            brand = brand.replace('S-Works', 'Specialized')
            return brand

        df.brand = df.brand.apply(brand_replace)

        # Resolve truncated brand names
        df.loc[df.brand == 'Santa', 'brand'] = 'Santa Cruz'  # Standardize Santa -> Santa Cruz
        df.loc[df.brand == 'We', 'brand'] = 'We The People'
        df.loc[df.brand == 'De', 'brand'] = 'De Rosa'

        return df

    @staticmethod
    def _parse_material(material: pd.Series) -> pd.Series:
        """Parse and normailize materials from data."""
        def material_replace(elem):
            # Skip np.NaN
            if not isinstance(elem, str) and math.isnan(elem):
                return elem

            materials_list = [
                'carbon', 'aluminum', 'aluminium', 'steel', 'alloy',
                'titanium', 'chromoly', 'crmo', 'cr-mo', 'hi-ten',
                'alluminum'
            ]
            materials_dict = {
                'carbon': 'carbon',
                'aluminium': 'aluminum',
                'aluminum': 'aluminum',
                'alloy': 'alloy',
                'steel': 'steel',
                'titanium': 'titanium',
                'chromoly': 'chromoly',
                'crmo': 'chromoly',
                'alluminum': 'aluminum',
                'cr-mo': 'chromoly',
                'hi-ten': 'steel'
            }
            for m in materials_list:
                if re.search(re.escape(m), elem, re.IGNORECASE):
                    return materials_dict[m]
            return np.NaN

        return material.apply(material_replace)

    def _parse_groupset(self, desc: pd.Series) -> pd.Series:
        """Return matched groupset types."""
        def groupset_replace(d, return_desc=True):
            # Skip np.NaN
            if not isinstance(d, str) and math.isnan(d):
                return d

            try:
                for groupset in self._GROUPSETS_MAP:
                    # remove ','
                    d = d.replace(',', '')
                    # Regex matching
                    if re.search(re.escape(groupset), d, re.IGNORECASE):
                        return self._GROUPSETS_MAP[groupset]
                    # # Extra custom cleaning
                    # others = {
                    #     'X01 Eagle': 'sram xO1 eagle',
                    #     'SEAM X01 Eagle': 'sram xO1 eagle',
                    #     'Sram A1': 'sram apex'
                    # }
                    # if d in others.keys():
                    #     return others[d]
            except AttributeError:
                pass
            return d if return_desc else np.NaN

        def brand_replace(d, return_desc=True):
            """Match for specific brands"""
            brands = ['praxis', 'oval', 'race face', 'fsa', 'sram stylo']

            try:
                # resolve some typos
                d = d.lower()
                d = d.replace('raceface', 'race face')
                for brand in brands:
                    if re.search(brand, d, re.IGNORECASE):
                        return brand

            except TypeError:
                pass
            except AttributeError:
                pass
            return d if return_desc else np.NaN

        # First parse from values
        parsed = desc.apply(groupset_replace, return_desc=False)

        # Second pass, fillnas when possible using specific logic
        for idx in parsed[parsed.isnull()].index:
            parsed[idx] = brand_replace(parsed[idx], return_desc=False)

        return parsed

    def _parse_cassette_type(self, desc: pd.Series) -> pd.Series:
        """Parse cassette groupset data."""
        # First pass using derailleur groupset logic
        groupset = self._parse_groupset(desc)

        def cassette_replace(d, return_desc=True):
            # Skip np.NaN
            if not isinstance(d, str) and math.isnan(d):
                return d

            cassette_map = {
                'sunrace': 'sunrace',
                'shimano hg500': 'shimano tiagra',
                'shimano hg 500': 'shimano tiagra',
                'shimano hg-500': 'shimano tiagra',
                'sram pg-1130': 'sram rival',
                'sram pg1130': 'sram rival',
                'sram pg 1130': 'sram rival',
                'sram xg 1150': 'sram gx',
                'sram xg1150': 'sram gx',
                'sram xg-1150': 'sram gx',
                'sram xg-1175': 'sram gx',
                'sram xg 1175': 'sram gx',
                'sram xg-175': 'sram gx',
                '1295 eagle': 'sram xO1 eagle',
                '1275 eagle': 'sram gx eagle',
                'sram xg-1190': 'sram red',
                'sram xg1190': 'sram red',
                'sram xg 1190': 'sram red',
                'shimano hg50': 'shimano sora',
                'shimano hg 50': 'shimano sora',
                'shimano hg-50': 'shimano sora',
                'shimano hg200': 'shimano tourney',
                'shimano hg 200': 'shimano tourney',
                'shimano hg-200': 'shimano tourney',
                'shimano hg-20': 'shimano tourney',
                'shimano hg 20': 'shimano tourney',
                'shimano hg20': 'shimano tourney',
                'shimano hg41': 'shimano acera',
                'shimano hg 41': 'shimano acera',
                'shimano hg-41': 'shimano acera',
                'flip flop': 'single speed',
                '22t steel': 'single speed',
                'fixed': 'single speed',
                'freewheel': 'single speed',
                'shimano hg31': 'shimano altus',
                'shimano hg-31': 'shimano altus',
                'shimano hg 31': 'shimano altus',
                'shimano hg-700': 'shimano 105',
                'shimano hg 700': 'shimano 105',
                'shimano hg700': 'shimano 105',
                'sram pg-1170': 'sram force',
                'sram pg1170': 'sram force',
                'sram pg 1170': 'sram force',
                'shimano hg400': 'shimano 9-speed',
                'shimano hg-400': 'shimano 9-speed',
                'shimano hg 400': 'shimano 9-speed',
                'hg 400': 'shimano 9-speed',
                'hg-400': 'shimano 9-speed',
                'hg400': 'shimano 9-speed',
                'shimano hg62': 'shimano deore',
                'shimano hg-62': 'shimano deore',
                'shimano hg 62': 'shimano deore',
                'shimano hg300': 'shimano alivio',
                'shimano hg-300': 'shimano alivio',
                'shimano hg 300': 'shimano alivio',
                'shimano 9s': 'shimano 9-speed',
                'sram pg970': 'sram 9-speed',
                'x01 eagle': 'sram xO1 eagle',
                'cs5700': 'shimano 105'
            }

            speeds_map = {
                'shimano.*7.{0,1}sp.{0,3}': 'shimano 7-speed',
                'shimano.*8.{0,1}sp.{0,3}': 'shimano 8-speed',
                'shimano.*9.{0,1}sp.{0,3}': 'shimano 9-speed',
                'shimano.*10.{0,1}sp.{0,3}': 'shimano 10-speed',
                'shimano.*11.{0,1}sp.{0,3}': 'shimano 11-speed',
                'sram.*7.{0,1}sp.{0,3}': 'sram 7-speed',
                'sram.*8.{0,1}sp.{0,3}': 'sram 8-speed',
                'sram.*9.{0,1}sp.{0,3}': 'sram 9-speed',
                'sram.*10.{0,1}sp.{0,3}': 'sram 10-speed',
                'sram.*11.{0,1}sp.{0,3}': 'sram 11-speed',
                'shimano.*5800': 'shimano 105',
                'shimano dura.{0,1}ace': 'shimano dura-ace',
                'sram.*1275': 'sram gx eagle',
                'sram.*pg.{0,1}1230': 'sram gx eagle',
                'sram.*xg.{0,1}1295': 'sram xO1 eagle',
                'sram .*1130': 'sram rival',
                'sram.*1299[ eagle]{0,1}': 'sram xx1 eagle',
                '\d{1,2}t cassett{0,1}e|cog': 'single speed',
                'hg.{0,1}200': 'shimano tourney'
            }

            try:
                # prelim clean
                d = d.lower()
                d = d.replace('cs-', '')
                d = d.replace('seam', 'sram')  # fix typo

                for cassette in cassette_map.keys():
                    # Regex literal search
                    if re.search(re.escape(cassette), d, re.IGNORECASE):
                        return cassette_map[cassette]

                # regex alternative search
                for cassette in speeds_map.keys():
                    if re.search(cassette, d, re.IGNORECASE):
                        return speeds_map[cassette]

            except AttributeError:
                pass
            return d if return_desc else np.NaN

        # Second pass, fillnas when possible using cassette specific logic
        for idx in groupset[groupset.isnull()].index:
            groupset[idx] = cassette_replace(groupset[idx], return_desc=False)

        return groupset

    @staticmethod
    def _parse_brake_type(field: pd.Series) -> pd.Series:
        """Categorize brake type by field value."""
        def brake_replace(brake):
            # Skip np.NaN
            if not isinstance(brake, str) and math.isnan(brake):
                return brake

            # Map specific components
            disc_components = ['sram guide', 'sram code', 'sram level',
                               'shimano xt', 'shimano slx', 'shimano deore',
                               'rotor', 'tektro md', 'spyre', 'shimano zee',
                               'rs505', 'hayes cx', 'r7070']
            for comp in disc_components:
                if re.search(re.escape(comp), brake, re.IGNORECASE):
                    brake = 'disc'
            hydraulic_comp = ['tektro hd', 'giant conduct', 'mt500', 'mt400',
                              'mt200', 'tektro m275']
            for comp in hydraulic_comp:
                if re.search(re.escape(comp), brake, re.IGNORECASE):
                    brake = 'hydraulic'
            caliper_components = ['shimano 105', 'shimano ultegra', 'br-5810',
                                  'pivot', 'long reach', 'trp', 'sram force',
                                  'sram rival', 'shimano sora', 'shimano tiagra',
                                  'shimano dura ace', 'tektro tk', 'tektro r312']
            for comp in caliper_components:
                if re.search(re.escape(comp), brake, re.IGNORECASE):
                    brake = 'caliper'
            if re.search(re.escape('direct pull'), brake, re.IGNORECASE):
                brake = 'v-brake'

            types_list = [
                'hydraulic', 'mechanical', 'rim', 'caliper', 'coaster',
                'disc', 'v-brake', 'u-brake', 'linear pull', 'linear-pull'
            ]
            normalize_map = {
                'linear pull': 'linear_pull',
                'linear-pull': 'linear_pull',
                'v-brake': 'vbrake',
                'u-brake': 'ubrake'
            }

            for material in types_list:
                if re.search(re.escape(material), brake, re.IGNORECASE):
                    return normalize_map.get(material, material)
            return brake  # 'other'

        return field.apply(brake_replace)

    def merge_source(self, source, bike_type='all'):
        """Return merged raw data files for given source."""
        manifest_rows = self._mediator.get_rows_matching(sources=[source],
                                                         bike_types=[bike_type])
        tablename_to_filename = dict()

        for row in manifest_rows:
            tablename = row['tablename']
            filename = self._mediator.get_filepath_for_manifest_row(row)
            tablename_to_filename[tablename] = filename

        # Get prods field for each specs data we have
        specs_df = pd.read_csv(tablename_to_filename['product_specs'])
        prods_df = pd.read_csv(tablename_to_filename['products'])
        merged_df = pd.merge(left=prods_df, right=specs_df, how='right', on=['product_id', 'site'])
        return merged_df

    def _create_munged_df(self, merged_df: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms merged df into munged df with necessary fields normalized.
        """
        # Initialize munged df with normalized base fields
        munged_df = merged_df.iloc[:, :8]
        munged_df = self._normalize_brands(munged_df)
        munged_df = self._fill_missing_bike_types(munged_df)
        munged_df = self._normalize_bike_type_values(munged_df)
        munged_df['model_year'] = self._parse_model_year(munged_df.description)

        # Populate other fields
        munged_df['frame_material'] = self._parse_material(merged_df.frame)
        munged_df['handlebar_material'] = self._parse_material(merged_df.handlebar)
        munged_df['fd_groupset'] = self._parse_groupset(merged_df.front_derailleur)
        munged_df['rd_groupset'] = self._parse_groupset(merged_df.rear_derailleur)
        munged_df['cassette_groupset'] = self._parse_cassette_type(merged_df.cassette)
        munged_df['crankset_material'] = self._parse_material(merged_df.crankset)
        munged_df['crankset_groupset'] = self._parse_groupset(merged_df.crankset)
        munged_df['brake_type'] = self._parse_brake_type(merged_df.brake_type)
        munged_df['seatpost_material'] = self._parse_material(merged_df.seatpost)
        munged_df['fork_material'] = self._parse_material(merged_df.fork)
        munged_df['chain_groupset'] = self._parse_material(merged_df.chain)
        munged_df['shifter_groupset'] = self._parse_material(merged_df.shifters)
        return munged_df

    def _save_munged_df(self, df: pd.DataFrame, source: str):
        """Save munged data frame to appropriate folder using source name."""
        f = os.path.join(self._save_data_path, f'{source}_munged.csv')
        df.to_csv(f, index=False, encoding='utf-8')

    def _jenson_cleaner(self, merged_df: pd.DataFrame,
                        to_csv=True) -> pd.DataFrame:
        """Cleaner for jenson raw data."""
        # Drop 'Unnamed: 0' column which is duplicate for 'brand'
        merged_df = merged_df.drop(labels='Unnamed: 0', axis=1)

        # Preliminary fill some NaNs from redundant columns
        merged_df.handlebar.fillna(merged_df.handlebars, inplace=True)
        merged_df.front_derailleur.fillna(merged_df.derailleurs, inplace=True)
        merged_df.rear_derailleur.fillna(merged_df.derailleurs, inplace=True)
        merged_df.weight.fillna(merged_df.approximate_weight, inplace=True)
        merged_df.shifters.fillna(merged_df.shifter, inplace=True)
        merged_df['brake_type'] = merged_df.brakes  # map to std field name
        merged_df.brake_type.fillna(merged_df.brake_levers, inplace=True)

        # Map 'corona_store_exclusives' bike type to 'intended_use'
        for idx in merged_df[merged_df.bike_type == 'corona_store_exclusives'].index:
            merged_df.bike_type[idx] = merged_df.intended_use[idx]

        munged_df = self._create_munged_df(merged_df=merged_df)

        if to_csv:
            self._save_munged_df(df=munged_df, source='jenson')

        return munged_df

    def _nashbar_cleaner(self, merged_df: pd.DataFrame,
                             to_csv=True) -> pd.DataFrame:
        """Cleaner for nashbar raw data."""
        # Drop 'Unnamed: 0' column which is duplicate for 'brand'
        merged_df = merged_df.drop(labels='Unnamed: 0', axis=1)

        # Preliminary fill some NaNs from redundant columns
        merged_df.weight.fillna(merged_df.frame_weight, inplace=True)
        merged_df['brake_type'] = merged_df.brakes  # map to std field name
        merged_df.brake_type.fillna(merged_df.brake_levers, inplace=True)
        merged_df.brake_type.fillna(merged_df.brakeset, inplace=True)
        merged_df.cassette.fillna(merged_df.cog, inplace=True)

        munged_df = self._create_munged_df(merged_df=merged_df)

        if to_csv:
            self._save_munged_df(df=munged_df, source='nashbar')

        return munged_df

    def _trek_cleaner(self, merged_df: pd.DataFrame,
                             to_csv=True) -> pd.DataFrame:
        """Cleaner for trek raw data."""
        # Preliminary fill some NaNs from redundant columns
        merged_df['brake_type'] = merged_df.brakeset  # map to std field name
        merged_df['crankset'] = merged_df.crank  # map to std field name

        munged_df = self._create_munged_df(merged_df=merged_df)

        if to_csv:
            self._save_munged_df(df=munged_df, source='trek')

        return munged_df

    def _rei_cleaner(self, merged_df: pd.DataFrame,
                        to_csv=True) -> pd.DataFrame:
        """Cleaner for rei raw data."""
        # Preliminary fill some NaNs from redundant columns
        merged_df.weight.fillna(merged_df.bike_weight, inplace=True)
        merged_df.brake_type.fillna(merged_df.brake_levers, inplace=True)
        merged_df.brake_type.fillna(merged_df.brakes, inplace=True)
        merged_df['cassette'] = merged_df.rear_cogs  # map to std field name
        merged_df.bike_type.fillna(merged_df.best_use, inplace=True)
        merged_df['seatpost'] = merged_df.seat_post

        # Map 'corona_store_exclusives' bike type to 'intended_use'
        for idx in merged_df[merged_df.bike_type == 'corona_store_exclusives'].index:
            merged_df.bike_type[idx] = merged_df.intended_use[idx]

        munged_df = self._create_munged_df(merged_df=merged_df)

        if to_csv:
            self._save_munged_df(df=munged_df, source='rei')

        return munged_df

    def _citybikes_cleaner(self, merged_df: pd.DataFrame,
                        to_csv=True) -> pd.DataFrame:
        """Cleaner for citybikes raw data."""
        # Preliminary fill some NaNs from redundant columns
        merged_df['brake_type'] = merged_df.brakes
        merged_df.brake_type.fillna(merged_df.brake_levers, inplace=True)
        merged_df['handlebar'] = merged_df.handlebars
        merged_df['cassette'] = merged_df.rear_cogs  # map to std field name
        merged_df.cassette.fillna(merged_df.cassette_rear_cogs, inplace=True)
        merged_df.cassette.fillna(merged_df.bicycle_drivetrain, inplace=True)
        merged_df.cassette.fillna(merged_df.chainrings, inplace=True)
        merged_df.crankset.fillna(merged_df.chainrings, inplace=True)
        merged_df.front_derailleur.fillna(merged_df.bicycle_drivetrain, inplace=True)
        merged_df.rear_derailleur.fillna(merged_df.bicycle_drivetrain, inplace=True)
        merged_df.seatpost.fillna(merged_df.seat_post, inplace=True)

        munged_df = self._create_munged_df(merged_df=merged_df)

        if to_csv:
            self._save_munged_df(df=munged_df, source='citybikes')

        return munged_df

    def _proshop_cleaner(self, merged_df: pd.DataFrame,
                        to_csv=True) -> pd.DataFrame:
        """Cleaner for proshop raw data."""
        # Preliminary fill some NaNs from redundant columns
        merged_df['brake_type'] = merged_df.brakes
        merged_df.brake_type.fillna(merged_df.brake_levers, inplace=True)
        merged_df['handlebar'] = merged_df.handlebars
        merged_df['cassette'] = merged_df.rear_cogs  # map to std field name
        merged_df.cassette.fillna(merged_df.cassette_rear_cogs, inplace=True)
        merged_df.cassette.fillna(merged_df.chainrings, inplace=True)
        merged_df.crankset.fillna(merged_df.chainrings, inplace=True)
        merged_df.cassette.fillna(merged_df.drive_system, inplace=True)
        merged_df.front_derailleur.fillna(merged_df.drive_system, inplace=True)
        merged_df.rear_derailleur.fillna(merged_df.drive_system, inplace=True)
        merged_df.seatpost.fillna(merged_df.seat_post, inplace=True)

        munged_df = self._create_munged_df(merged_df=merged_df)

        if to_csv:
            self._save_munged_df(df=munged_df, source='proshop')

        return munged_df

    def _contebikes_cleaner(self, merged_df: pd.DataFrame,
                        to_csv=True) -> pd.DataFrame:
        """Cleaner for contebikes raw data."""
        # Preliminary fill some NaNs from redundant columns
        merged_df['brake_type'] = merged_df.brakes
        merged_df.brake_type.fillna(merged_df.brake_levers, inplace=True)
        merged_df['handlebar'] = merged_df.handlebars
        merged_df['cassette'] = merged_df.rear_cogs  # map to std field name
        merged_df.cassette.fillna(merged_df.cassette_rear_cogs, inplace=True)
        merged_df.cassette.fillna(merged_df.chainrings, inplace=True)
        merged_df.crankset.fillna(merged_df.chainrings, inplace=True)
        merged_df.cassette.fillna(merged_df.drive_system, inplace=True)
        merged_df.front_derailleur.fillna(merged_df.drive_system, inplace=True)
        merged_df.rear_derailleur.fillna(merged_df.drive_system, inplace=True)
        merged_df.seatpost.fillna(merged_df.seat_post, inplace=True)

        munged_df = self._create_munged_df(merged_df=merged_df)

        if to_csv:
            self._save_munged_df(df=munged_df, source='contebikes')

        return munged_df

    def _eriks_cleaner(self, merged_df: pd.DataFrame,
                        to_csv=True) -> pd.DataFrame:
        """Cleaner for eriks raw data."""
        # Preliminary fill some NaNs from redundant columns
        merged_df['brake_type'] = merged_df.brakes
        merged_df.brake_type.fillna(merged_df.brake_levers, inplace=True)
        merged_df.brake_type.fillna(merged_df.front_and_rear_brakes, inplace=True)
        merged_df.brake_type.fillna(merged_df.front_brake, inplace=True)
        merged_df.brake_type.fillna(merged_df.rear_brake, inplace=True)
        merged_df.brake_type.fillna(merged_df.brake_rotor, inplace=True)
        merged_df.brake_type.fillna(merged_df.brake_rotors, inplace=True)
        merged_df.brake_type.fillna(merged_df.disc_rotor, inplace=True)
        merged_df.brake_type.fillna(merged_df.rotor, inplace=True)
        merged_df.brake_type.fillna(merged_df.rotors, inplace=True)
        merged_df.handlebar.fillna(merged_df.handlebars, inplace=True)
        merged_df.cassette.fillna(merged_df.cog, inplace=True)
        merged_df.cassette.fillna(merged_df.freewheel_cassette, inplace=True)
        merged_df.cassette.fillna(merged_df.drivetrain, inplace=True)
        merged_df.cassette.fillna(merged_df.cogset, inplace=True)
        merged_df.crankset.fillna(merged_df.crank_set, inplace=True)
        merged_df.crankset.fillna(merged_df.cranks, inplace=True)
        merged_df.crankset.fillna(merged_df.crank_arm_set, inplace=True)
        merged_df.crankset.fillna(merged_df.chainrings, inplace=True)
        merged_df.crankset.fillna(merged_df.drivetrain, inplace=True)
        merged_df.front_derailleur.fillna(merged_df.drivetrain, inplace=True)
        merged_df.rear_derailleur.fillna(merged_df.drivetrain, inplace=True)
        merged_df.shifters.fillna(merged_df.shifter, inplace=True)
        merged_df.shifters.fillna(merged_df.derailleur_shifter, inplace=True)
        merged_df.shifters.fillna(merged_df.derailleur_shifters, inplace=True)
        merged_df['seatpost'] = merged_df.seat_post
        merged_df.frame.fillna(merged_df.material, inplace=True)

        munged_df = self._create_munged_df(merged_df=merged_df)

        if to_csv:
            self._save_munged_df(df=munged_df, source='eriks')

        return munged_df

    def _canyon_cleaner(self, merged_df: pd.DataFrame,
                        to_csv=True) -> pd.DataFrame:
        """Cleaner for canyon raw data."""
        # Preliminary fill some NaNs from redundant columns
        merged_df['brake_type'] = merged_df.brakes
        merged_df.brake_type.fillna(merged_df.brake_levers, inplace=True)
        merged_df.brake_type.fillna(merged_df.brake_shift_levers, inplace=True)
        merged_df['crankset'] = merged_df.cranks
        merged_df.crankset.fillna(merged_df.chainrings, inplace=True)
        merged_df['seatpost'] = merged_df.seat_post

        munged_df = self._create_munged_df(merged_df=merged_df)

        if to_csv:
            self._save_munged_df(df=munged_df, source='canyon')

        return munged_df

    def _giant_cleaner(self, merged_df: pd.DataFrame,
                        to_csv=True) -> pd.DataFrame:
        """Cleaner for giant raw data."""
        # Preliminary fill some NaNs from redundant columns
        merged_df['brake_type'] = merged_df.brakes
        merged_df.brake_type.fillna(merged_df.brake_levers, inplace=True)

        munged_df = self._create_munged_df(merged_df=merged_df)

        if to_csv:
            self._save_munged_df(df=munged_df, source='giant')

        return munged_df

    def _litespeed_cleaner(self, merged_df: pd.DataFrame,
                           to_csv=True) -> pd.DataFrame:
        """Cleaner for litespeed raw data."""
        # Preliminary fill some NaNs from redundant columns
        merged_df['brake_type'] = merged_df.brakes
        merged_df.brake_type.fillna(merged_df.brakeset, inplace=True)
        merged_df.shifters.fillna(merged_df.rear_shifter, inplace=True)
        merged_df['frame'] = ['titanium'] * merged_df.shape[0]

        munged_df = self._create_munged_df(merged_df=merged_df)

        if to_csv:
            self._save_munged_df(df=munged_df, source='litespeed')

        return munged_df

    def _lynskey_cleaner(self, merged_df: pd.DataFrame,
                           to_csv=True) -> pd.DataFrame:
        """Cleaner for lynskey raw data."""
        # Preliminary fill some NaNs from redundant columns
        merged_df['brake_type'] = merged_df.lever_brakeset
        merged_df.brake_type.fillna(merged_df.lever_brakeset, inplace=True)
        merged_df.brake_type.fillna(merged_df.lever_brake, inplace=True)
        merged_df.brake_type.fillna(merged_df.brake_calipers, inplace=True)
        merged_df.brake_type.fillna(merged_df.disc_brake_calipers, inplace=True)
        merged_df.crankset.fillna(merged_df.chainring, inplace=True)
        merged_df['frame'] = merged_df.frame_material
        merged_df['shifters'] = merged_df.shifter

        munged_df = self._create_munged_df(merged_df=merged_df)

        if to_csv:
            self._save_munged_df(df=munged_df, source='lynskey')

        return munged_df

    def _spokes_cleaner(self, merged_df: pd.DataFrame,
                           to_csv=True) -> pd.DataFrame:
        """Cleaner for spokes raw data."""
        # Preliminary fill some NaNs from redundant columns
        merged_df['brake_type'] = merged_df.brakes
        merged_df.brake_type.fillna(merged_df.brake_levers, inplace=True)
        merged_df.brake_type.fillna(merged_df.brake_compatibility, inplace=True)
        merged_df['handlebar'] = merged_df.handlebars
        merged_df['cassette'] = merged_df.rear_cogs  # map to std field name
        merged_df.cassette.fillna(merged_df.cassette_rear_cogs, inplace=True)
        merged_df.cassette.fillna(merged_df.chainrings, inplace=True)
        merged_df.crankset.fillna(merged_df.chainrings, inplace=True)
        merged_df.cassette.fillna(merged_df.drive_system, inplace=True)
        merged_df.front_derailleur.fillna(merged_df.drive_system, inplace=True)
        merged_df.rear_derailleur.fillna(merged_df.drive_system, inplace=True)
        merged_df.seatpost.fillna(merged_df.seat_post, inplace=True)

        munged_df = self._create_munged_df(merged_df=merged_df)

        if to_csv:
            self._save_munged_df(df=munged_df, source='spokes')

        return munged_df

    def _specialized_cleaner(self, merged_df: pd.DataFrame,
                             to_csv=True) -> pd.DataFrame:
        """Cleaner for specialized raw data."""
        # Preliminary fill some NaNs from redundant columns
        merged_df['brake_type'] = merged_df.brake_levers  # map to std field name
        merged_df.brake_type.fillna(merged_df.front_brake, inplace=True)
        merged_df.brake_type.fillna(merged_df.rear_brake, inplace=True)
        merged_df.brake_type.fillna(merged_df.front_wheel, inplace=True)
        merged_df.brake_type.fillna(merged_df.rear_wheel, inplace=True)
        merged_df.crankset.fillna(merged_df.chainrings, inplace=True)
        merged_df['shifters'] = merged_df.shift_levers  # map to std field name
        merged_df['handlebar'] = merged_df.handlebars

        munged_df = self._create_munged_df(merged_df=merged_df)

        if to_csv:
            self._save_munged_df(df=munged_df, source='specialized')

        return munged_df

    def _backcountry_cleaner(self, merged_df: pd.DataFrame,
                             to_csv=True) -> pd.DataFrame:
        """Cleaner for backcountry raw data."""
        # Preliminary fill some NaNs from redundant columns
        merged_df.brake_type.fillna(merged_df.brakeset, inplace=True)
        merged_df['frame'] = merged_df.frame_material  # map to std field name

        munged_df = self._create_munged_df(merged_df=merged_df)

        if to_csv:
            self._save_munged_df(df=munged_df, source='backcountry')
        return munged_df

    def _competitive_cleaner(self, merged_df: pd.DataFrame,
                             to_csv=True) -> pd.DataFrame:
        """Cleaner for competitive raw data."""
        # Drop 'Unnamed: 0' column which is duplicate for 'brand'
        merged_df = merged_df.drop(labels='Unnamed: 0', axis=1)

        # Preliminary fill some NaNs from redundant columns
        merged_df.handlebar.fillna(merged_df.handlebars, inplace=True)
        merged_df.front_derailleur.fillna(merged_df.derailleurs, inplace=True)
        merged_df.rear_derailleur.fillna(merged_df.derailleurs, inplace=True)
        merged_df.weight.fillna(merged_df.approximate_weight, inplace=True)
        merged_df.shifters.fillna(merged_df.shifter, inplace=True)
        merged_df['brake_type'] = merged_df.brakes  # map to std field name
        merged_df.brake_type.fillna(merged_df.brake_levers, inplace=True)

        munged_df = self._create_munged_df(merged_df=merged_df)

        if to_csv:
            self._save_munged_df(df=munged_df, source='competitive')

        return munged_df


