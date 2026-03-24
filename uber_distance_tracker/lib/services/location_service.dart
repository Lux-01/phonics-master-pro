import 'dart:async';
import 'dart:math' show cos, sqrt, atan2, sin, pi;
import 'package:geolocator/geolocator.dart';
import 'package:flutter_foreground_task/flutter_foreground_task.dart';
import 'database_service.dart';
import '../models/session.dart';

class LocationService {
  static final LocationService _instance = LocationService._internal();
  factory LocationService() => _instance;
  LocationService._internal();

  final DatabaseService _db = DatabaseService();
  StreamSubscription<Position>? _positionStream;
  DrivingSession? _currentSession;
  Position? _lastPosition;
  
  final _distanceController = StreamController<double>.broadcast();
  Stream<double> get distanceStream => _distanceController.stream;

  bool get isTracking => _currentSession != null && _currentSession!.isActive;

  Future<void> startTracking() async {
    if (isTracking) return;

    // Check location permission
    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        throw Exception('Location permission denied');
      }
    }

    if (permission == LocationPermission.deniedForever) {
      throw Exception('Location permission permanently denied');
    }

    // Get initial position
    final initialPosition = await Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.high,
    );

    // Create new session
    _currentSession = DrivingSession(
      startTime: DateTime.now(),
      startLat: initialPosition.latitude,
      startLng: initialPosition.longitude,
    );

    // Save to database
    final id = await _db.insertSession(_currentSession!);
    _currentSession = _currentSession!.copyWith(id: id);

    // Start foreground service
    await _startForegroundService();

    // Start listening to location updates
    _positionStream = Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 10, // Update every 10 meters
      ),
    ).listen(_onLocationUpdate);

    _lastPosition = initialPosition;
  }

  Future<void> stopTracking() async {
    if (!isTracking) return;

    // Get final position
    final finalPosition = await Geolocator.getCurrentPosition();

    // Update session
    _currentSession = _currentSession!.copyWith(
      endTime: DateTime.now(),
      endLat: finalPosition.latitude,
      endLng: finalPosition.longitude,
    );

    await _db.updateSession(_currentSession!);

    // Stop location stream
    await _positionStream?.cancel();
    _positionStream = null;

    // Stop foreground service
    await _stopForegroundService();

    _lastPosition = null;
    _currentSession = null;
  }

  void _onLocationUpdate(Position position) {
    if (_lastPosition == null || _currentSession == null) {
      _lastPosition = position;
      return;
    }

    // Calculate distance from last position
    final distance = _calculateDistance(
      _lastPosition!.latitude,
      _lastPosition!.longitude,
      position.latitude,
      position.longitude,
    );

    // Only add if moved more than 5 meters (filter GPS noise)
    if (distance > 0.005) {
      _currentSession = _currentSession!.copyWith(
        totalDistanceKm: _currentSession!.totalDistanceKm + distance,
      );
      
      _db.updateSession(_currentSession!);
      _distanceController.add(_currentSession!.totalDistanceKm);
    }

    _lastPosition = position;
  }

  double _calculateDistance(double lat1, double lon1, double lat2, double lon2) {
    const double R = 6371; // Earth's radius in kilometers
    
    final double dLat = _toRadians(lat2 - lat1);
    final double dLon = _toRadians(lon2 - lon1);
    
    final double a = sin(dLat / 2) * sin(dLat / 2) +
        cos(_toRadians(lat1)) * cos(_toRadians(lat2)) *
        sin(dLon / 2) * sin(dLon / 2);
    
    final double c = 2 * atan2(sqrt(a), sqrt(1 - a));
    
    return R * c;
  }

  double _toRadians(double degrees) {
    return degrees * (pi / 180);
  }

  Future<void> _startForegroundService() async {
    await FlutterForegroundTask.startService(
      notificationTitle: 'Uber Distance Tracker',
      notificationText: 'Tracking your trip...',
      callback: startCallback,
    );
  }

  Future<void> _stopForegroundService() async {
    await FlutterForegroundTask.stopService();
  }

  void dispose() {
    _distanceController.close();
    _positionStream?.cancel();
  }
}

// This callback function must be a top-level function
@pragma('vm:entry-point')
void startCallback() {
  FlutterForegroundTask.setTaskHandler(LocationTaskHandler());
}

class LocationTaskHandler extends TaskHandler {
  @override
  Future<void> onStart(DateTime timestamp) async {
    // Service started
  }

  @override
  Future<void> onEvent(DateTime timestamp, SendPort? sendPort) async {
    // Periodic events if needed
  }

  @override
  Future<void> onDestroy(DateTime timestamp) async {
    // Service destroyed
  }

  @override
  void onButtonPressed(String id) {
    // Handle notification button presses
  }
}
