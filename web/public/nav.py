# -*- coding: utf-8 -*-

from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator

nav = Nav()

nav.register_element('frontend_top', Navbar(
    View('FS.lv', 'main.index'),
    Subgroup(
        'Cars',
        Text('Timeline'),

        View('Price vs Year', 'cars.price_vs_year'),
        View('Mileage vs Year', 'cars.mileage_vs_year'),
        View('Number vs Year', 'cars.bar_price_counts_by_year'),
        View('Market Cap vs Year', 'cars.bar_price_sum_by_year'),
        View('Mean price vs Year', 'cars.bar_price_mean_by_year'),
        View('Colors vs Year', 'cars.bar_color_by_year'),

        Separator(),
        Text('Empty'),
    ),
    Subgroup(
        'Flats',
        Text('Riga Districts'),

        View('Price vs District', 'flats.box_riga_price_mean_by_district'),

        View('Average price per m2 vs District', 'flats.bar_riga_avg_price_m2_by_district'),
        View('Average price vs District', 'flats.bar_riga_avg_price_by_district'),
        View('Average area vs District', 'flats.bar_riga_avg_area_by_district'),
        View('New, USSR or Other vs District', 'flats.bar_riga_supply_by_district'),

        Separator(),
        Text('Riga Prices'),

        View('Area vs Price', 'flats.scatter_riga_area_by_price'),
    ),
))
