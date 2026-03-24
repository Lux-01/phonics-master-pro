# Uber Distance Tracker - Kivy Version
# This creates a native Android APK using Buildozer

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
from kivy.graphics import Color, RoundedRectangle

import json
import os
from datetime import datetime
from math import radians, cos, sin, asin, sqrt

# Android-specific imports (only work on Android)
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.runnable import run_on_ui_thread
    from jnius import autoclass
    import gps

# Database file
DB_FILE = 'trips.json'

class TripCard(BoxLayout):
    """Custom widget for displaying a trip"""
    def __init__(self, trip_data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 80
        self.padding = 10
        self.spacing = 10
        
        # Background
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # Icon
        icon = Label(
            text='🚗',
            font_size=30,
            size_hint_x=None,
            width=50
        )
        self.add_widget(icon)
        
        # Info
        info = BoxLayout(orientation='vertical')
        distance = trip_data.get('distance', 0)
        if distance < 1:
            dist_text = f"{int(distance * 1000)} m"
        else:
            dist_text = f"{distance:.2f} km"
        
        date_str = datetime.fromisoformat(trip_data['start_time']).strftime('%b %d, %Y')
        
        info.add_widget(Label(
            text=dist_text,
            font_size=18,
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            halign='left'
        ))
        info.add_widget(Label(
            text=date_str,
            font_size=12,
            color=(0.4, 0.4, 0.4, 1),
            halign='left'
        ))
        self.add_widget(info)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class UberTrackerApp(App):
    """Main App Class"""
    
    # Properties for data binding
    is_tracking = BooleanProperty(False)
    current_distance = NumericProperty(0.0)
    total_distance = NumericProperty(0.0)
    total_trips = NumericProperty(0)
    status_text = StringProperty('Ready to start')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.trips = []
        self.current_trip = None
        self.last_pos = None
        self.gps_event = None
        
        # Set window color
        Window.clearcolor = (0.965, 0.973, 0.98, 1)  # #F6F8FA
    
    def build(self):
        """Build the UI"""
        self.load_trips()
        
        # Main layout
        root = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = Label(
            text='📍 Distance Tracker',
            font_size=24,
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=50
        )
        root.add_widget(header)
        
        # Stats row
        stats = GridLayout(cols=2, spacing=15, size_hint_y=None, height=120)
        
        # Total Distance Card
        self.dist_card = self.create_stat_card('0.0 km', 'Total Distance', '🛣️', (0.153, 0.431, 0.945, 1))
        stats.add_widget(self.dist_card)
        
        # Total Trips Card
        self.trips_card = self.create_stat_card('0', 'Trips', '🚗', (0.02, 0.58, 0.31, 1))
        stats.add_widget(self.trips_card)
        
        root.add_widget(stats)
        
        # Active trip display (shown when tracking)
        self.active_display = self.create_active_display()
        root.add_widget(self.active_display)
        
        # Start/Stop Button
        self.action_btn = Button(
            text='START TRIP',
            font_size=20,
            bold=True,
            background_color=(0.02, 0.58, 0.31, 1),  # Green
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=70
        )
        self.action_btn.bind(on_press=self.toggle_tracking)
        root.add_widget(self.action_btn)
        
        # Recent trips label
        root.add_widget(Label(
            text='Recent Trips',
            font_size=18,
            bold=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=30,
            halign='left'
        ))
        
        # Trips list
        self.trips_container = BoxLayout(orientation='vertical', spacing=10)
        scroll = ScrollView()
        scroll.add_widget(self.trips_container)
        root.add_widget(scroll)
        
        self.update_stats()
        self.refresh_trips_list()
        
        return root
    
    def create_stat_card(self, value, label, icon, color):
        """Create a stat card widget"""
        card = BoxLayout(orientation='vertical', padding=15, spacing=5)
        card.canvas.before.add(Color(1, 1, 1, 1))
        card.rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
        card.canvas.before.add(card.rect)
        card.bind(pos=self.update_card_rect, size=self.update_card_rect)
        
        # Icon
        card.add_widget(Label(
            text=icon,
            font_size=30,
            size_hint_y=None,
            height=40
        ))
        
        # Value
        value_label = Label(
            text=value,
            font_size=22,
            bold=True,
            color=(0.1, 0.1, 0.1, 1)
        )
        card.value_label = value_label
        card.add_widget(value_label)
        
        # Label
        card.add_widget(Label(
            text=label,
            font_size=12,
            color=(0.4, 0.4, 0.4, 1)
        ))
        
        return card
    
    def update_card_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size
    
    def create_active_display(self):
        """Create the active trip display"""
        box = BoxLayout(orientation='vertical', padding=20, spacing=10, size_hint_y=None, height=150)
        box.canvas.before.add(Color(0.153, 0.431, 0.945, 1))  # Blue
        box.rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[20])
        box.canvas.before.add(box.rect)
        box.bind(pos=self.update_card_rect, size=self.update_card_rect)
        
        # Header
        header = BoxLayout(size_hint_y=None, height=30)
        header.add_widget(Label(text='●', color=(1, 1, 1, 0.7), size_hint_x=None, width=20))
        header.add_widget(Label(
            text='TRIP IN PROGRESS',
            color=(1, 1, 1, 0.7),
            font_size=12,
            bold=True
        ))
        box.add_widget(header)
        
        # Distance
        self.live_distance_label = Label(
            text='0.00 km',
            font_size=36,
            bold=True,
            color=(1, 1, 1, 1)
        )
        box.add_widget(self.live_distance_label)
        
        box.opacity = 0  # Hidden initially
        return box
    
    def toggle_tracking(self, instance):
        """Start or stop tracking"""
        if self.is_tracking:
            self.stop_tracking()
        else:
            self.start_tracking()
    
    def start_tracking(self):
        """Start GPS tracking"""
        if platform == 'android':
            # Request permissions
            request_permissions([
                Permission.ACCESS_FINE_LOCATION,
                Permission.ACCESS_COARSE_LOCATION
            ])
        
        # Create new trip
        self.current_trip = {
            'start_time': datetime.now().isoformat(),
            'distance': 0.0,
            'positions': []
        }
        
        self.is_tracking = True
        self.current_distance = 0.0
        self.last_pos = None
        
        # Update UI
        self.action_btn.text = 'STOP TRIP'
        self.action_btn.background_color = (0.882, 0.098, 0, 1)  # Red
        self.active_display.opacity = 1
        
        # Start GPS
        if platform == 'android':
            try:
                gps.configure(on_location=self.on_gps_location)
                gps.start(minTime=3000, minDistance=10)  # 3 seconds, 10 meters
            except Exception as e:
                print(f"GPS Error: {e}")
        else:
            # Simulate on desktop
            self.gps_event = Clock.schedule_interval(self.simulate_gps, 2.0)
        
        # Update display every second
        Clock.schedule_interval(self.update_live_display, 1.0)
    
    def stop_tracking(self):
        """Stop tracking and save trip"""
        self.is_tracking = False
        
        # Stop GPS
        if platform == 'android':
            try:
                gps.stop()
            except:
                pass
        else:
            if self.gps_event:
                self.gps_event.cancel()
        
        # Save trip
        if self.current_trip:
            self.current_trip['end_time'] = datetime.now().isoformat()
            self.current_trip['distance'] = self.current_distance
            self.trips.insert(0, self.current_trip)
            self.save_trips()
        
        # Reset
        self.current_trip = None
        self.current_distance = 0.0
        self.last_pos = None
        
        # Update UI
        self.action_btn.text = 'START TRIP'
        self.action_btn.background_color = (0.02, 0.58, 0.31, 1)  # Green
        self.active_display.opacity = 0
        
        self.update_stats()
        self.refresh_trips_list()
    
    def on_gps_location(self, **kwargs):
        """Handle GPS location update"""
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        
        if lat and lon:
            self.process_position(lat, lon)
    
    def simulate_gps(self, dt):
        """Simulate GPS movement for testing"""
        import random
        if self.last_pos:
            # Add small random movement
            lat = self.last_pos[0] + random.uniform(-0.0001, 0.0001)
            lon = self.last_pos[1] + random.uniform(-0.0001, 0.0001)
        else:
            # Default to Sydney
            lat = -33.8688
            lon = 151.2093
        
        self.process_position(lat, lon)
    
    def process_position(self, lat, lon):
        """Process new GPS position"""
        if self.last_pos:
            # Calculate distance
            distance = self.haversine(
                self.last_pos[0], self.last_pos[1],
                lat, lon
            )
            
            # Only add if moved more than 5 meters
            if distance > 0.005:
                self.current_distance += distance
                self.current_trip['positions'].append({
                    'lat': lat,
                    'lon': lon,
                    'time': datetime.now().isoformat()
                })
        
        self.last_pos = (lat, lon)
    
    def haversine(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two GPS points"""
        R = 6371  # Earth radius in km
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        return R * c
    
    def update_live_display(self, dt):
        """Update the live distance display"""
        if self.is_tracking:
            if self.current_distance < 1:
                text = f"{int(self.current_distance * 1000)} m"
            else:
                text = f"{self.current_distance:.2f} km"
            self.live_distance_label.text = text
    
    def update_stats(self):
        """Update statistics display"""
        total = sum(t.get('distance', 0) for t in self.trips)
        self.total_distance = total
        self.total_trips = len(self.trips)
        
        # Update cards
        if total < 1:
            self.dist_card.value_label.text = f"{int(total * 1000)} m"
        else:
            self.dist_card.value_label.text = f"{total:.1f} km"
        
        self.trips_card.value_label.text = str(self.total_trips)
    
    def refresh_trips_list(self):
        """Refresh the trips list"""
        self.trips_container.clear_widgets()
        
        if not self.trips:
            self.trips_container.add_widget(Label(
                text='No trips yet',
                color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height=100
            ))
        else:
            for trip in self.trips[:20]:  # Show last 20
                self.trips_container.add_widget(TripCard(trip))
    
    def load_trips(self):
        """Load trips from file"""
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, 'r') as f:
                    self.trips = json.load(f)
            except:
                self.trips = []
        else:
            self.trips = []
    
    def save_trips(self):
        """Save trips to file"""
        with open(DB_FILE, 'w') as f:
            json.dump(self.trips, f)

# Run the app
if __name__ == '__main__':
    UberTrackerApp().run()
