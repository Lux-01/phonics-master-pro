class DrivingSession {
  final int? id;
  final DateTime startTime;
  final DateTime? endTime;
  final double totalDistanceKm;
  final double? startLat;
  final double? startLng;
  final double? endLat;
  final double? endLng;
  final String? notes;

  DrivingSession({
    this.id,
    required this.startTime,
    this.endTime,
    this.totalDistanceKm = 0.0,
    this.startLat,
    this.startLng,
    this.endLat,
    this.endLng,
    this.notes,
  });

  bool get isActive => endTime == null;
  String get duration {
    final end = endTime ?? DateTime.now();
    final diff = end.difference(startTime);
    final hours = diff.inHours;
    final minutes = diff.inMinutes % 60;
    if (hours > 0) {
      return '${hours}h ${minutes}m';
    }
    return '${minutes}m';
  }

  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'startTime': startTime.toIso8601String(),
      'endTime': endTime?.toIso8601String(),
      'totalDistanceKm': totalDistanceKm,
      'startLat': startLat,
      'startLng': startLng,
      'endLat': endLat,
      'endLng': endLng,
      'notes': notes,
    };
  }

  factory DrivingSession.fromMap(Map<String, dynamic> map) {
    return DrivingSession(
      id: map['id'] as int?,
      startTime: DateTime.parse(map['startTime'] as String),
      endTime: map['endTime'] != null 
          ? DateTime.parse(map['endTime'] as String) 
          : null,
      totalDistanceKm: (map['totalDistanceKm'] as num).toDouble(),
      startLat: map['startLat'] as double?,
      startLng: map['startLng'] as double?,
      endLat: map['endLat'] as double?,
      endLng: map['endLng'] as double?,
      notes: map['notes'] as String?,
    );
  }

  DrivingSession copyWith({
    int? id,
    DateTime? startTime,
    DateTime? endTime,
    double? totalDistanceKm,
    double? startLat,
    double? startLng,
    double? endLat,
    double? endLng,
    String? notes,
  }) {
    return DrivingSession(
      id: id ?? this.id,
      startTime: startTime ?? this.startTime,
      endTime: endTime ?? this.endTime,
      totalDistanceKm: totalDistanceKm ?? this.totalDistanceKm,
      startLat: startLat ?? this.startLat,
      startLng: startLng ?? this.startLng,
      endLat: endLat ?? this.endLat,
      endLng: endLng ?? this.endLng,
      notes: notes ?? this.notes,
    );
  }
}
