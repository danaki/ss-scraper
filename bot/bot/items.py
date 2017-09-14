# -*- coding: utf-8 -*-

from datetime import datetime

from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import *
from mongoengine_item import MongoengineItem


class BaseDocument(Document):
    meta = {
        'abstract': True,
        'indexes': [
            {
                'fields': ['open', 'price_period']
            }
    }
    _changes = ListField(DictField())

    open = BooleanField(default=True, required=True)
    found = DateTimeField()
    crawled = DateTimeField(default=datetime.now)

    url = URLField()
    views = IntField()
    created = DateTimeField()
    highlighted = BooleanField()
    text_length = IntField()
    text_rus_ratio = IntField()

    price = FloatField()
    price_period = StringField()


class Car(BaseDocument):
    meta = {
        'indexes': [
            {
                'fields': ['open', 'price_period', 'production_year', 'mileage']
            }
        ]
    }

    brand = StringField()
    model = StringField()
    production_year = IntField()
    production_month = StringField()
    engine_fuel = StringField()
    engine_volume = FloatField()
    body_type = StringField()
    color = StringField()
    gearbox = StringField()
    inspection_month = IntField()
    inspection_year = IntField()
    location = StringField()
    mileage = IntField()
    vin = StringField()

    audio_video_bluetooth = BooleanField()
    audio_video_cd_changer = BooleanField()
    audio_video_cd_player = BooleanField()
    audio_video_dvd_player = BooleanField()
    audio_video_dvd_changer = BooleanField()
    audio_video_fm_am = BooleanField()
    audio_video_handsfree_kit = BooleanField()
    audio_video_hdd = BooleanField()
    audio_video_lcd_monitor = BooleanField()
    audio_video_mp3_player = BooleanField()
    audio_video_navigation_gps = BooleanField()
    audio_video_sdcard = BooleanField()
    audio_video_subwoofer = BooleanField()
    audio_video_tv = BooleanField()
    audio_video_usb_input = BooleanField()
    climate_air_conditioning = BooleanField()
    climate_autonomous_heater = BooleanField()
    climate_cabin_air_filter = BooleanField()
    climate_climate_control = BooleanField()
    driven_wheels_all_wheel_4_4 = BooleanField()
    electronics_adaptive_cruise_control = BooleanField()
    electronics_autodimming_mirrors = BooleanField()
    electronics_blind_spot_assist = BooleanField()
    electronics_brake_assist = BooleanField()
    electronics_cruise_control = BooleanField()
    electronics_distance_sensors = BooleanField()
    electronics_electric_door_opener = BooleanField()
    electronics_electric_mirrors = BooleanField()
    electronics_electric_mirrors_with_memory = BooleanField()
    electronics_electric_trunk_release = BooleanField()
    electronics_electrically_adjustable_steering_wheel = BooleanField()
    electronics_front_parking_sensor = BooleanField()
    electronics_heated_steering_wheel = BooleanField()
    electronics_heated_mirrors = BooleanField()
    electronics_in_car_mobile_phone = BooleanField()
    electronics_keyless_go = BooleanField()
    electronics_lane_assist = BooleanField()
    electronics_night_vision_camera = BooleanField()
    electronics_on_board_computer = BooleanField()
    electronics_pedestrian_detection = BooleanField()
    electronics_rainfall_sensor = BooleanField()
    electronics_rear_electric_sunshade = BooleanField()
    electronics_rear_parking_sensor = BooleanField()
    electronics_rear_view_camera = BooleanField()
    electronics_retractable_mirrors = BooleanField()
    electronics_self_parking = BooleanField()
    electronics_sport_mirrors = BooleanField()
    electronics_start_stop_system = BooleanField()
    electronics_tyre_pressure_monitoring = BooleanField()
    electronics_traffic_sign_recognition = BooleanField()
    exterior_adaptive_high_beam_assist = BooleanField()
    exterior_additional_brake_lights = BooleanField()
    exterior_automatic_daytime_running_lights = BooleanField()
    exterior_automatic_high_beams = BooleanField()
    exterior_bi_xenon_lights = BooleanField()
    exterior_fog_lights = BooleanField()
    exterior_footboards = BooleanField()
    exterior_headlights_washers = BooleanField()
    exterior_led_brake_lights = BooleanField()
    exterior_led_daytime_running_lights = BooleanField()
    exterior_light_alloy_rims = BooleanField()
    exterior_roof_rack = BooleanField()
    exterior_tow_hook = BooleanField()
    exterior_xenon_lights = BooleanField()
    interior_adjustable_steering_wheel = BooleanField()
    interior_armrests = BooleanField()
    interior_electric_power_steering = BooleanField()
    interior_electric_seats = BooleanField()
    interior_electric_seats_with_memory = BooleanField()
    interior_fridge = BooleanField()
    interior_heated_seats = BooleanField()
    interior_hydraulic_power_steering = BooleanField()
    interior_isofix_guides = BooleanField()
    interior_leather_seats = BooleanField()
    interior_massage_seats = BooleanField()
    interior_multifunctional_steering_wheel = BooleanField()
    interior_panoramic_roof = BooleanField()
    interior_recaro_seats = BooleanField()
    interior_sport_seats = BooleanField()
    interior_sport_steering_wheel = BooleanField()
    interior_steering_wheel_with_memory = BooleanField()
    interior_sunroof = BooleanField()
    interior_tinted_windows = BooleanField()
    interior_ventilated_front_seats = BooleanField()
    interior_window_shutters = BooleanField()
    other_service_book = BooleanField()
    safety_360_degree_camera = BooleanField()
    safety_abs = BooleanField()
    safety_airbags = BooleanField()
    safety_esp = BooleanField()
    safety_traction_control_system = BooleanField()
    security_alarm = BooleanField()
    security_central_locking = BooleanField()
    security_immobilizer = BooleanField()
    security_marking = BooleanField()
    tuning_air_suspension = BooleanField()
    tuning_spoiler = BooleanField()
    tuning_sports_package = BooleanField()


class Flat(BaseDocument):
    meta = {
        'indexes': [
            {
                'fields': ['open', 'production_year', 'mileage']
            }
        ]
    }

    city = StringField()
    district = StringField()
    village = StringField()
    street = StringField()
    rooms = IntField()
    area = FloatField()
    floor = IntField()
    floors_total = IntField()
    lift = BooleanField()
    project = StringField()
    building_type = StringField()
    conveniences = StringField()


class CarItem(MongoengineItem):
    mongoengine_model = Car

class FlatItem(MongoengineItem):
    mongoengine_model = Flat

