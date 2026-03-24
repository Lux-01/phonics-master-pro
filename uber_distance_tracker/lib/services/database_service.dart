import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../models/session.dart';

class DatabaseService {
  static final DatabaseService _instance = DatabaseService._internal();
  static Database? _database;

  factory DatabaseService() => _instance;

  DatabaseService._internal();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final databasesPath = await getDatabasesPath();
    final path = join(databasesPath, 'uber_tracker.db');

    return await openDatabase(
      path,
      version: 1,
      onCreate: _onCreate,
    );
  }

  Future<void> _onCreate(Database db, int version) async {
    await db.execute('''
      CREATE TABLE sessions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        startTime TEXT NOT NULL,
        endTime TEXT,
        totalDistanceKm REAL NOT NULL DEFAULT 0,
        startLat REAL,
        startLng REAL,
        endLat REAL,
        endLng REAL,
        notes TEXT
      )
    ''');
  }

  Future<int> insertSession(DrivingSession session) async {
    final db = await database;
    return await db.insert('sessions', session.toMap());
  }

  Future<void> updateSession(DrivingSession session) async {
    final db = await database;
    await db.update(
      'sessions',
      session.toMap(),
      where: 'id = ?',
      whereArgs: [session.id],
    );
  }

  Future<List<DrivingSession>> getAllSessions() async {
    final db = await database;
    final List<Map<String, dynamic>> maps = await db.query(
      'sessions',
      orderBy: 'startTime DESC',
    );
    return List.generate(maps.length, (i) => DrivingSession.fromMap(maps[i]));
  }

  Future<DrivingSession?> getActiveSession() async {
    final db = await database;
    final List<Map<String, dynamic>> maps = await db.query(
      'sessions',
      where: 'endTime IS NULL',
      limit: 1,
    );
    if (maps.isNotEmpty) {
      return DrivingSession.fromMap(maps.first);
    }
    return null;
  }

  Future<void> deleteSession(int id) async {
    final db = await database;
    await db.delete(
      'sessions',
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<Map<String, dynamic>> getStats() async {
    final db = await database;
    final sessions = await getAllSessions();
    
    double totalKm = 0;
    int totalSessions = 0;
    int totalMinutes = 0;
    
    for (var session in sessions) {
      if (session.endTime != null) {
        totalKm += session.totalDistanceKm;
        totalSessions++;
        totalMinutes += session.endTime!.difference(session.startTime).inMinutes;
      }
    }

    return {
      'totalKm': totalKm,
      'totalSessions': totalSessions,
      'totalHours': (totalMinutes / 60).toStringAsFixed(1),
    };
  }
}
