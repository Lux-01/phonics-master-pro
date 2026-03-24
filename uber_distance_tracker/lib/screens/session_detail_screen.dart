import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/session.dart';

class SessionDetailScreen extends StatelessWidget {
  final DrivingSession session;

  const SessionDetailScreen({super.key, required this.session});

  String _formatDistance(double km) {
    if (km < 1) {
      return '${(km * 1000).toStringAsFixed(0)} meters';
    }
    return '${km.toStringAsFixed(2)} kilometers';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF6F8FA),
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.transparent,
        title: const Text('Trip Details'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Distance Card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFF276EF1), Color(0xFF1E54B7)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Column(
                children: [
                  const Text(
                    'Total Distance',
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _formatDistance(session.totalDistanceKm),
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 42,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Details Card
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Trip Information',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 20),
                    _buildDetailRow(
                      'Start Time',
                      DateFormat('MMM d, yyyy h:mm a').format(session.startTime),
                      Icons.play_circle_outline,
                    ),
                    const Divider(height: 24),
                    if (session.endTime != null) ...[
                      _buildDetailRow(
                        'End Time',
                        DateFormat('MMM d, yyyy h:mm a').format(session.endTime!),
                        Icons.stop_circle_outlined,
                      ),
                      const Divider(height: 24),
                    ],
                    _buildDetailRow(
                      'Duration',
                      session.duration,
                      Icons.timer_outlined,
                    ),
                    const Divider(height: 24),
                    _buildDetailRow(
                      'Status',
                      session.isActive ? 'In Progress' : 'Completed',
                      session.isActive ? Icons.sync : Icons.check_circle,
                      valueColor: session.isActive ? Colors.orange : Colors.green,
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Location Card
            if (session.startLat != null && session.startLng != null)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Location Data',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 20),
                      _buildDetailRow(
                        'Start Location',
                        '${session.startLat!.toStringAsFixed(6)}, ${session.startLng!.toStringAsFixed(6)}',
                        Icons.location_on_outlined,
                      ),
                      if (session.endLat != null && session.endLng != null) ...[
                        const Divider(height: 24),
                        _buildDetailRow(
                          'End Location',
                          '${session.endLat!.toStringAsFixed(6)}, ${session.endLng!.toStringAsFixed(6)}',
                          Icons.location_off_outlined,
                        ),
                      ],
                    ],
                  ),
                ),
              ),

            const SizedBox(height: 32),

            // Actions
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      // Share trip data
                      final text = '''
Trip Summary:
Distance: ${_formatDistance(session.totalDistanceKm)}
Duration: ${session.duration}
Date: ${DateFormat('MMM d, yyyy').format(session.startTime)}
                      '''.trim();
                      
                      // Share functionality would go here
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Share functionality coming soon')),
                      );
                    },
                    icon: const Icon(Icons.share),
                    label: const Text('Share'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      Navigator.pop(context);
                    },
                    icon: const Icon(Icons.arrow_back),
                    label: const Text('Back'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value, IconData icon, {Color? valueColor}) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: const Color(0xFF276EF1).withOpacity(0.1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(
            icon,
            color: const Color(0xFF276EF1),
            size: 20,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
              const SizedBox(height: 2),
              Text(
                value,
                style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w500,
                  color: valueColor,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
