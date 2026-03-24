# Uber Distance Tracker - Google Colab Build Script
# Run this in Google Colab to build the APK for free

# Step 1: Mount Google Drive (to save APK)
from google.colab import drive
drive.mount('/content/drive')

print("✅ Google Drive mounted")

# Step 2: Install dependencies
!apt-get update -qq
!apt-get install -y -qq \
    git zip unzip openjdk-17-jdk python3-pip \
    autoconf libtool pkg-config zlib1g-dev \
    libncurses5-dev libncursesw5-dev libffi-dev \
    libssl-dev libsqlite3-dev libgdbm-dev \
    libreadline-dev libbz2-dev

print("✅ System dependencies installed")

# Step 3: Install buildozer
!pip3 install -q buildozer cython

print("✅ Buildozer installed")

# Step 4: Create project directory
!mkdir -p /content/uber_tracker_kivy
%cd /content/uber_tracker_kivy

# Step 5: Create main.py
main_py = '''
# Uber Distance Tracker - Kivy Version
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
from kivy.graphics import Color, RoundedRectangle

import json
import os
from datetime import datetime
from math import radians, cos, sin, asin, sqrt

if platform == 'android':
    from android.permissions import request_permissions, Permission
    import gps

DB_FILE = 'trips.json'

class TripCard(BoxLayout):
    def __init__(self, trip_data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 80
        self.padding = 10
        self.spacing = 10
        
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        icon = Label(text='🚗', font_size=30, size_hint_x=None, width=50)
        self.add_widget(icon)
        
        info = BoxLayout(orientation='vertical')
        distance = trip_data.get('distance', 0)
        dist_text = f"{int(distance * 1000)} m" if distance < 1 else f"{distance:.2f} km"
        date_str = datetime.fromisoformat(trip_data['start_time']).strftime('%b %d, %Y')
        
        info.add_widget(Label(text=dist_text, font_size=18, bold=True, color=(0.1, 0.1, 0.1, 1), halign='left'))
        info.add_widget(Label(text=date_str, font_size=12, color=(0.4, 0.4, 0.4, 1), halign='left'))
        self.add_widget(info)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class UberTrackerApp(App):
    is_tracking = BooleanProperty(False)
    current_distance = NumericProperty(0.0)
    total_distance = NumericProperty(0.0)
    total_trips = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.trips = []
        self.current_trip = None
        self.last_pos = None
        self.gps_event = None
        Window.clearcolor = (0.965, 0.973, 0.98, 1)
    
    def build(self):
        self.load_trips()
        
        root = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        root.add_widget(Label(text='📍 Distance Tracker', font_size=24, bold=True, 
                              color=(0.1, 0.1, 0.1, 1), size_hint_y=None, height=50))
        
        # Stats
        stats = GridLayout(cols=2, spacing=15, size_hint_y=None, height=120)
        self.dist_card = self.create_stat_card('0.0 km', 'Total Distance', '🛣️', (0.153, 0.431, 0.945, 1))
        stats.add_widget(self.dist_card)
        self.trips_card = self.create_stat_card('0', 'Trips', '🚗', (0.02, 0.58, 0.31, 1))
        stats.add_widget(self.trips_card)
        root.add_widget(stats)
        
        # Active display
        self.active_display = self.create_active_display()
        root.add_widget(self.active_display)
        
        # Action button
        self.action_btn = Button(text='START TRIP', font_size=20, bold=True,
                                   background_color=(0.02, 0.58, 0.31, 1), color=(1, 1, 1, 1),
                                   size_hint_y=None, height=70)
        self.action_btn.bind(on_press=self.toggle_tracking)
        root.add_widget(self.action_btn)
        
        # Trips list
        root.add_widget(Label(text='Recent Trips', font_size=18, bold=True, 
                              color=(0.1, 0.1, 0.1, 1), size_hint_y=None, height=30, halign='left'))
        
        self.trips_container = BoxLayout(orientation='vertical', spacing=10)
        scroll = ScrollView()
        scroll.add_widget(self.trips_container)
        root.add_widget(scroll)
        
        self.update_stats()
        self.refresh_trips_list()
        
        return root
    
    def create_stat_card(self, value, label, icon, color):
        card = BoxLayout(orientation='vertical', padding=15, spacing=5)
        with card.canvas.before:
            Color(1, 1, 1, 1)
            card.rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
        card.bind(pos=lambda obj, val: setattr(card.rect, 'pos', val),
                  size=lambda obj, val: setattr(card.rect, 'size', val))
        
        card.add_widget(Label(text=icon, font_size=30, size_hint_y=None, height=40))
        value_label = Label(text=value, font_size=22, bold=True, color=(0.1, 0.1, 0.1, 1))
        card.value_label = value_label
        card.add_widget(value_label)
        card.add_widget(Label(text=label, font_size=12, color=(0.4, 0.4, 0.4, 1)))
        return card
    
    def create_active_display(self):
        box = BoxLayout(orientation='vertical', padding=20, spacing=10, size_hint_y=None, height=150)
        with box.canvas.before:
            Color(0.153, 0.431, 0.945, 1)
            box.rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[20])
        box.bind(pos=lambda obj, val: setattr(box.rect, 'pos', val),
                 size=lambda obj, val: setattr(box.rect, 'size', val))
        
        header = BoxLayout(size_hint_y=None, height=30)
        header.add_widget(Label(text='●', color=(1, 1, 1, 0.7), size_hint_x=None, width=20))
        header.add_widget(Label(text='TRIP IN PROGRESS', color=(1, 1, 1, 0.7), font_size=12, bold=True))
        box.add_widget(header)
        
        self.live_distance_label = Label(text='0.00 km', font_size=36, bold=True, color=(1, 1, 1, 1))
        box.add_widget(self.live_distance_label)
        box.opacity = 0
        return box
    
    def toggle_tracking(self, instance):
        if self.is_tracking:
            self.stop_tracking()
        else:
            self.start_tracking()
    
    def start_tracking(self):
        if platform == 'android':
            request_permissions([Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION])
        
        self.current_trip = {'start_time': datetime.now().isoformat(), 'distance': 0.0, 'positions': []}
        self.is_tracking = True
        self.current_distance = 0.0
        self.last_pos = None
        
        self.action_btn.text = 'STOP TRIP'
        self.action_btn.background_color = (0.882, 0.098, 0, 1)
        self.active_display.opacity = 1
        
        if platform == 'android':
            try:
                gps.configure(on_location=self.on_gps_location)
                gps.start(minTime=3000, minDistance=10)
            except Exception as e:
                print(f"GPS Error: {e}")
        else:
            self.gps_event = Clock.schedule_interval(self.simulate_gps, 2.0)
        
        Clock.schedule_interval(self.update_live_display, 1.0)
    
    def stop_tracking(self):
        self.is_tracking = False
        
        if platform == 'android':
            try:
                gps.stop()
            except:
                pass
        else:
            if self.gps_event:
                self.gps_event.cancel()
        
        if self.current_trip:
            self.current_trip['end_time'] = datetime.now().isoformat()
            self.current_trip['distance'] = self.current_distance
            self.trips.insert(0, self.current_trip)
            self.save_trips()
        
        self.current_trip = None
        self.current_distance = 0.0
        self.last_pos = None
        
        self.action_btn.text = 'START TRIP'
        self.action_btn.background_color = (0.02, 0.58, 0.31, 1)
        self.active_display.opacity = 0
        
        self.update_stats()
        self.refresh_trips_list()
    
    def on_gps_location(self, **kwargs):
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        if lat and lon:
            self.process_position(lat, lon)
    
    def simulate_gps(self, dt):
        import random
        if self.last_pos:
            lat = self.last_pos[0] + random.uniform(-0.0001, 0.0001)
            lon = self.last_pos[1] + random.uniform(-0.0001, 0.0001)
        else:
            lat, lon = -33.8688, 151.2093
        self.process_position(lat, lon)
    
    def process_position(self, lat, lon):
        if self.last_pos:
            distance = self.haversine(self.last_pos[0], self.last_pos[1], lat, lon)
            if distance > 0.005:
                self.current_distance += distance
                self.current_trip['positions'].append({'lat': lat, 'lon': lon, 'time': datetime.now().isoformat()})
        self.last_pos = (lat, lon)
    
    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat, dlon = lat2 - lat1, lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        return R * 2 * asin(sqrt(a))
    
    def update_live_display(self, dt):
        if self.is_tracking:
            text = f"{int(self.current_distance * 1000)} m" if self.current_distance < 1 else f"{self.current_distance:.2f} km"
            self.live_distance_label.text = text
    
    def update_stats(self):
        total = sum(t.get('distance', 0) for t in self.trips)
        self.total_distance = total
        self.total_trips = len(self.trips)
        self.dist_card.value_label.text = f"{int(total * 1000)} m" if total < 1 else f"{total:.1f} km"
        self.trips_card.value_label.text = str(self.total_trips)
    
    def refresh_trips_list(self):
        self.trips_container.clear_widgets()
        if not self.trips:
            self.trips_container.add_widget(Label(text='No trips yet', color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=100))
        else:
            for trip in self.trips[:20]:
                self.trips_container.add_widget(TripCard(trip))
    
    def load_trips(self):
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, 'r') as f:
                    self.trips = json.load(f)
            except:
                self.trips = []
        else:
            self.trips = []
    
    def save_trips(self):
        with open(DB_FILE, 'w') as f:
            json.dump(self.trips, f)

if __name__ == '__main__':
    UberTrackerApp().run()
'''

with open('/content/uber_tracker_kivy/main.py', 'w') as f:
    f.write(main_py)

print("✅ main.py created")

# Step 6: Create buildozer.spec
buildozer_spec = '''
[app]
title = Uber Distance Tracker
package.name = ubertracker
package.domain = com.ubertracker
source.dir = .
version = 1.0
requirements = python3,kivy,plyer
android.requirements = android,pyjnius
orientation = portrait
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,ACCESS_NETWORK_STATE,WAKE_LOCK
android.features = android.hardware.location,android.hardware.location.gps
android.fullscreen = 0
android.archs = arm64-v8a,armeabi-v7a

[buildozer]
log_level = 2
build_dir = ./.buildozer
bin_dir = ./bin
'''

with open('/content/uber_tracker_kivy/buildozer.spec', 'w') as f:
    f.write(buildozer_spec)

print("✅ buildozer.spec created")

# Step 7: Build APK
print("🔨 Building APK (this will take 20-40 minutes)...")
print("⏳ First build downloads Android SDK and NDK...")
print("")

%cd /content/uber_tracker_kivy
!buildozer android debug 2>&1 | tee build.log

# Step 8: Copy APK to Google Drive
print("")
print("📦 Copying APK to Google Drive...")
!mkdir -p /content/drive/MyDrive/UberTracker
!cp bin/*.apk /content/drive/MyDrive/UberTracker/ 2>/dev/null || echo "No APK found in bin/"
!ls -la /content/drive/MyDrive/UberTracker/

print("")
print("✅ Done!")
print("📱 Check your Google Drive in the UberTracker folder")
print("   for the APK file")
