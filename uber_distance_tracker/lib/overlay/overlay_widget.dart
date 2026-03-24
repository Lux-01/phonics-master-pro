import 'package:flutter/material.dart';
import 'package:flutter_overlay_window/flutter_overlay_window.dart';
import '../services/location_service.dart';

// This is the overlay widget that appears as a floating button
// It stays on top of other apps so the driver can see it while using maps

class OverlayWidget extends StatefulWidget {
  const OverlayWidget({super.key});

  @override
  State<OverlayWidget> createState() => _OverlayWidgetState();
}

class _OverlayWidgetState extends State<OverlayWidget> {
  final LocationService _locationService = LocationService();
  double _distance = 0.0;
  bool _isTracking = false;

  @override
  void initState() {
    super.initState();
    _checkStatus();
    
    // Listen to distance updates
    _locationService.distanceStream.listen((distance) {
      if (mounted) {
        setState(() {
          _distance = distance;
        });
      }
    });
  }

  Future<void> _checkStatus() async {
    // Check if there's an active session
    setState(() {
      _isTracking = _locationService.isTracking;
    });
  }

  String _formatDistance(double km) {
    if (km < 1) {
      return '${(km * 1000).toStringAsFixed(0)}m';
    }
    return '${km.toStringAsFixed(1)}km';
  }

  Future<void> _toggleTracking() async {
    if (_isTracking) {
      await _locationService.stopTracking();
    } else {
      try {
        await _locationService.startTracking();
      } catch (e) {
        // Handle error silently in overlay
      }
    }
    setState(() {
      _isTracking = !_isTracking;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: Container(
        width: 140,
        height: 60,
        decoration: BoxDecoration(
          color: _isTracking 
              ? const Color(0xFFE11900).withOpacity(0.95)
              : const Color(0xFF05944F).withOpacity(0.95),
          borderRadius: BorderRadius.circular(30),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.3),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Distance display
            if (_isTracking) ...[
              Text(
                _formatDistance(_distance),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(width: 8),
            ],
            
            // Start/Stop button
            GestureDetector(
              onTap: _toggleTracking,
              child: Container(
                width: 44,
                height: 44,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.2),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  _isTracking ? Icons.stop : Icons.play_arrow,
                  color: Colors.white,
                  size: 24,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Service to manage the overlay
class OverlayService {
  static final OverlayService _instance = OverlayService._internal();
  factory OverlayService() => _instance;
  OverlayService._internal();

  bool _isOverlayActive = false;

  Future<void> showOverlay() async {
    if (_isOverlayActive) return;

    final bool status = await FlutterOverlayWindow.isActive();
    if (!status) {
      await FlutterOverlayWindow.showOverlay(
        height: 60,
        width: 140,
        alignment: OverlayAlignment.bottomRight,
        visibility: NotificationVisibility.visibilityPublic,
        enableDrag: true,
        positionGravity: PositionGravity.none,
      );
      _isOverlayActive = true;
    }
  }

  Future<void> hideOverlay() async {
    if (!_isOverlayActive) return;

    final bool status = await FlutterOverlayWindow.isActive();
    if (status) {
      await FlutterOverlayWindow.closeOverlay();
      _isOverlayActive = false;
    }
  }

  Future<void> updateOverlayPosition(OverlayAlignment alignment) async {
    await FlutterOverlayWindow.showOverlay(
      alignment: alignment,
    );
  }

  bool get isOverlayActive => _isOverlayActive;
}
