"""
Flask Backend API for AI Recommendation Engine
Provides RESTful endpoints for user management, preferences, and recommendations.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import sys

# Add backend directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database as db
from recommendation import (
    get_content_based_recommendations, 
    get_categories,
    get_category_distribution,
    get_trending_categories
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

# ==================== HEALTH & ROOT ENDPOINTS ====================

@app.route('/', methods=['GET'])
def index():
    """Root endpoint - API information."""
    return jsonify({
        'name': 'AI Recommendation Engine API',
        'version': '1.0.0',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'health': '/health',
            'categories': '/categories',
            'recommend': 'POST /recommend',
            'save_user': 'POST /save_user',
            'history': '/history',
            'users': '/users',
            'analytics': '/analytics',
            'export': '/export/<table>'
        }
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        users = db.get_all_users()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


# ==================== CATEGORY ENDPOINTS ====================

@app.route('/categories', methods=['GET'])
def categories():
    """Get all available categories."""
    try:
        cats = get_categories()
        return jsonify({
            'success': True,
            'categories': cats,
            'count': len(cats)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/trending', methods=['GET'])
def trending():
    """Get trending categories."""
    try:
        trending_cats = get_trending_categories()
        return jsonify({
            'success': True,
            'trending': trending_cats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== USER ENDPOINTS ====================

@app.route('/save_user', methods=['POST'])
def save_user():
    """Create or get a user."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        username = data.get('username')
        email = data.get('email')
        
        if not username or not email:
            return jsonify({
                'success': False, 
                'error': 'Username and email are required'
            }), 400
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400
        
        # Check if user exists
        existing_user = db.get_user_by_username(username)
        
        if existing_user:
            # Return existing user
            preferences = db.get_user_preferences(existing_user['id'])
            return jsonify({
                'success': True,
                'user': existing_user,
                'preferences': preferences,
                'message': 'User already exists'
            })
        
        # Create new user
        user = db.create_user(username, email)
        
        return jsonify({
            'success': True,
            'user': user,
            'preferences': [],
            'message': 'User created successfully'
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/users', methods=['GET'])
def get_users():
    """Get all users."""
    try:
        users = db.get_all_users()
        return jsonify({
            'success': True,
            'users': users,
            'count': len(users)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/users/search', methods=['GET'])
def search_users():
    """Search users by query."""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400
        
        users = db.search_users(query)
        return jsonify({
            'success': True,
            'users': users,
            'count': len(users)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user."""
    try:
        success = db.delete_user(user_id)
        if success:
            return jsonify({
                'success': True,
                'message': f'User {user_id} deleted successfully'
            })
        return jsonify({
            'success': False,
            'error': 'User not found'
        }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== PREFERENCE ENDPOINTS ====================

@app.route('/preferences/<int:user_id>', methods=['GET'])
def get_preferences(user_id):
    """Get preferences for a user."""
    try:
        preferences = db.get_user_preferences(user_id)
        distribution = get_category_distribution(preferences)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'preferences': preferences,
            'distribution': distribution
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/preferences', methods=['POST'])
def save_preferences():
    """Save preferences for a user."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        user_id = data.get('user_id')
        preferences = data.get('preferences', [])
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        if not preferences:
            return jsonify({
                'success': False,
                'error': 'preferences array is required'
            }), 400
        
        # Validate preferences format
        for pref in preferences:
            if 'category' not in pref or 'rating' not in pref:
                return jsonify({
                    'success': False,
                    'error': 'Each preference must have category and rating'
                }), 400
            
            rating = pref['rating']
            if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
                return jsonify({
                    'success': False,
                    'error': 'Rating must be between 1 and 5'
                }), 400
        
        # Save preferences
        saved = db.save_preferences(user_id, preferences)
        
        return jsonify({
            'success': True,
            'message': 'Preferences saved successfully',
            'saved_preferences': saved
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== RECOMMENDATION ENDPOINTS ====================

@app.route('/recommend', methods=['POST'])
def recommend():
    """
    Main recommendation endpoint.
    Accepts user preferences and returns top 5 recommendations.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        user_id = data.get('user_id')
        preferences = data.get('preferences', [])
        top_n = data.get('top_n', 5)
        
        if not preferences:
            return jsonify({
                'success': False,
                'error': 'preferences array is required'
            }), 400
        
        # Validate preferences
        for pref in preferences:
            if 'category' not in pref or 'rating' not in pref:
                return jsonify({
                    'success': False,
                    'error': 'Each preference must have category and rating'
                }), 400
            
            rating = pref['rating']
            if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
                return jsonify({
                    'success': False,
                    'error': 'Rating must be between 1 and 5'
                }), 400
        
        # Generate recommendations
        recommendations = get_content_based_recommendations(preferences, top_n)
        
        # Save to database if user_id provided
        if user_id:
            db.save_recommendations(user_id, recommendations)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'total': len(recommendations),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/history/<int:user_id>', methods=['GET'])
def get_history(user_id):
    """Get recommendation history for a user."""
    try:
        recommendations = db.get_user_recommendations(user_id)
        return jsonify({
            'success': True,
            'user_id': user_id,
            'recommendations': recommendations,
            'total': len(recommendations)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/history', methods=['GET'])
def get_all_history():
    """Get all recommendation history (admin)."""
    try:
        recommendations = db.get_all_recommendations()
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'total': len(recommendations)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== ANALYTICS ENDPOINTS ====================

@app.route('/analytics', methods=['GET'])
def analytics():
    """Get analytics data."""
    try:
        stats = db.get_recommendation_stats()
        all_prefs = db.get_all_preferences()
        
        # Category distribution
        cat_dist = {}
        for pref in all_prefs:
            cat = pref['category']
            cat_dist[cat] = cat_dist.get(cat, 0) + 1
        
        # Rating distribution
        rating_dist = {}
        for pref in all_prefs:
            rating = pref['rating']
            rating_dist[rating] = rating_dist.get(rating, 0) + 1
        
        # Trending categories
        trending_cats = get_trending_categories()
        
        return jsonify({
            'success': True,
            'stats': stats,
            'category_distribution': cat_dist,
            'rating_distribution': rating_dist,
            'trending_categories': trending_cats,
            'total_users': len(db.get_all_users()),
            'total_preferences': len(all_prefs)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== EXPORT ENDPOINTS ====================

@app.route('/export/<table>', methods=['GET'])
def export_data(table):
    """Export table data as CSV-friendly JSON."""
    try:
        valid_tables = ['users', 'preferences', 'recommendations']
        
        if table not in valid_tables:
            return jsonify({
                'success': False,
                'error': f'Invalid table. Must be one of: {valid_tables}'
            }), 400
        
        data = db.export_to_csv(table)
        
        return jsonify({
            'success': True,
            'table': table,
            'data': data,
            'count': len(data)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/',
            '/health',
            '/categories',
            '/recommend (POST)',
            '/save_user (POST)',
            '/history/<user_id>',
            '/users',
            '/analytics',
            '/export/<table>'
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors."""
    return jsonify({
        'success': False,
        'error': 'Bad request'
    }), 400


# ==================== MAIN ====================

if __name__ == '__main__':
    # Ensure database is initialized
    db.init_db()
    
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    )
