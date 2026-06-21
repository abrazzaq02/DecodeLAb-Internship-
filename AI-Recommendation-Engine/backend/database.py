"""
Database Module for AI Recommendation Engine
Handles all SQLite database operations including CRUD for users, preferences, and recommendations.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'recommendation.db')


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """Initialize the database with all required tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Recommendations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                category TEXT NOT NULL,
                similarity_score REAL NOT NULL,
                match_percentage REAL NOT NULL,
                description TEXT,
                rank INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        print("[DB] Database initialized successfully")


# ==================== USER OPERATIONS ====================

def create_user(username: str, email: str) -> Dict[str, Any]:
    """Create a new user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (username, email) VALUES (?, ?)',
                (username, email)
            )
            conn.commit()
            user_id = cursor.lastrowid
            return {
                'id': user_id,
                'username': username,
                'email': email,
                'created_at': datetime.now().isoformat()
            }
        except sqlite3.IntegrityError as e:
            raise ValueError(f"User already exists: {str(e)}")


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Get user by username."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_all_users() -> List[Dict[str, Any]]:
    """Get all users."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
        return [dict(row) for row in cursor.fetchall()]


def search_users(query: str) -> List[Dict[str, Any]]:
    """Search users by username or email."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM users WHERE username LIKE ? OR email LIKE ? ORDER BY created_at DESC',
            (f'%{query}%', f'%{query}%')
        )
        return [dict(row) for row in cursor.fetchall()]


def delete_user(user_id: int) -> bool:
    """Delete a user and all related data."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        return cursor.rowcount > 0


# ==================== PREFERENCE OPERATIONS ====================

def save_preference(user_id: int, category: str, rating: int) -> Dict[str, Any]:
    """Save or update a user preference."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Check if preference already exists
        cursor.execute(
            'SELECT id FROM preferences WHERE user_id = ? AND category = ?',
            (user_id, category)
        )
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute(
                'UPDATE preferences SET rating = ? WHERE user_id = ? AND category = ?',
                (rating, user_id, category)
            )
        else:
            cursor.execute(
                'INSERT INTO preferences (user_id, category, rating) VALUES (?, ?, ?)',
                (user_id, category, rating)
            )
        
        conn.commit()
        return {
            'user_id': user_id,
            'category': category,
            'rating': rating,
            'updated_at': datetime.now().isoformat()
        }


def save_preferences(user_id: int, preferences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Save multiple preferences for a user."""
    results = []
    for pref in preferences:
        result = save_preference(user_id, pref['category'], pref['rating'])
        results.append(result)
    return results


def get_user_preferences(user_id: int) -> List[Dict[str, Any]]:
    """Get all preferences for a user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM preferences WHERE user_id = ? ORDER BY rating DESC',
            (user_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_all_preferences() -> List[Dict[str, Any]]:
    """Get all preferences."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM preferences ORDER BY created_at DESC')
        return [dict(row) for row in cursor.fetchall()]


def delete_preference(pref_id: int) -> bool:
    """Delete a preference."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM preferences WHERE id = ?', (pref_id,))
        conn.commit()
        return cursor.rowcount > 0


# ==================== RECOMMENDATION OPERATIONS ====================

def save_recommendation(user_id: int, item_name: str, category: str, 
                        similarity_score: float, match_percentage: float,
                        description: str, rank: int) -> Dict[str, Any]:
    """Save a recommendation."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO recommendations 
               (user_id, item_name, category, similarity_score, match_percentage, description, rank) 
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (user_id, item_name, category, similarity_score, match_percentage, description, rank)
        )
        conn.commit()
        rec_id = cursor.lastrowid
        return {
            'id': rec_id,
            'user_id': user_id,
            'item_name': item_name,
            'category': category,
            'similarity_score': similarity_score,
            'match_percentage': match_percentage,
            'description': description,
            'rank': rank,
            'timestamp': datetime.now().isoformat()
        }


def save_recommendations(user_id: int, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Save multiple recommendations."""
    results = []
    for rec in recommendations:
        result = save_recommendation(
            user_id=user_id,
            item_name=rec['item_name'],
            category=rec['category'],
            similarity_score=rec['similarity_score'],
            match_percentage=rec['match_percentage'],
            description=rec.get('description', ''),
            rank=rec['rank']
        )
        results.append(result)
    return results


def get_user_recommendations(user_id: int) -> List[Dict[str, Any]]:
    """Get all recommendations for a user."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM recommendations WHERE user_id = ? ORDER BY timestamp DESC',
            (user_id,)
        )
        return [dict(row) for row in cursor.fetchall()]


def get_all_recommendations() -> List[Dict[str, Any]]:
    """Get all recommendations."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM recommendations ORDER BY timestamp DESC')
        return [dict(row) for row in cursor.fetchall()]


def get_recommendation_stats() -> Dict[str, Any]:
    """Get recommendation statistics."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Total recommendations
        cursor.execute('SELECT COUNT(*) as total FROM recommendations')
        total = cursor.fetchone()['total']
        
        # Total unique users
        cursor.execute('SELECT COUNT(DISTINCT user_id) as total_users FROM recommendations')
        total_users = cursor.fetchone()['total_users']
        
        # Most popular category
        cursor.execute('''
            SELECT category, COUNT(*) as count 
            FROM recommendations 
            GROUP BY category 
            ORDER BY count DESC 
            LIMIT 1
        ''')
        row = cursor.fetchone()
        popular_category = row['category'] if row else None
        
        # Average similarity score
        cursor.execute('SELECT AVG(similarity_score) as avg_score FROM recommendations')
        avg_score = cursor.fetchone()['avg_score'] or 0
        
        return {
            'total_recommendations': total,
            'total_users': total_users,
            'most_popular_category': popular_category,
            'average_similarity_score': round(avg_score, 4)
        }


def delete_recommendation(rec_id: int) -> bool:
    """Delete a recommendation."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM recommendations WHERE id = ?', (rec_id,))
        conn.commit()
        return cursor.rowcount > 0


# ==================== EXPORT OPERATIONS ====================

def export_to_csv(table_name: str) -> List[Dict[str, Any]]:
    """Export a table to CSV-friendly format."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM {table_name} ORDER BY id')
        return [dict(row) for row in cursor.fetchall()]


# Initialize database on module import
init_db()
