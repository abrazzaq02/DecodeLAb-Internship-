# AI Recommendation Engine

A complete production-ready AI Recommendation System built with Flask (Backend API) and React (Frontend Dashboard). The system uses content-based filtering with cosine similarity to deliver personalized recommendations based on user interests and ratings.

![AI Recommendation Engine](https://img.shields.io/badge/AI-Recommendation%20Engine-cyan?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-Backend-green?style=for-the-badge&logo=flask)
![React](https://img.shields.io/badge/React-Frontend-blue?style=for-the-badge&logo=react)
![SQLite](https://img.shields.io/badge/SQLite-Database-orange?style=for-the-badge&logo=sqlite)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-orange?style=for-the-badge)

## Features

### User Preference Panel
- Multi-select interest categories
- 9 technology categories: AI, ML, Deep Learning, Computer Vision, NLP, Data Science, Web Development, Cyber Security, Cloud Computing
- Star rating system (1-5) for each category
- Save and update preferences

### Recommendation Engine
- Content-based filtering algorithm
- Cosine similarity computation using TF-IDF vectorization
- Top 5 personalized recommendations
- Similarity score display (0-1 scale)
- Match percentage visualization
- Confidence indicators

### Flask API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/categories` | Get all categories |
| GET | `/trending` | Get trending categories |
| POST | `/save_user` | Create/update user |
| GET | `/users` | List all users |
| GET | `/users/search?q=` | Search users |
| DELETE | `/users/<id>` | Delete user |
| POST | `/preferences` | Save preferences |
| GET | `/preferences/<user_id>` | Get user preferences |
| POST | `/recommend` | Get recommendations |
| GET | `/history/<user_id>` | User recommendation history |
| GET | `/history` | All recommendation history |
| GET | `/analytics` | Analytics data |
| GET | `/export/<table>` | Export data as CSV |

### Dashboard UI
- Dark theme with neon accent effects
- Glassmorphism design components
- Cursor spotlight light effect
- Animated gradient background with floating orbs
- Interactive recommendation cards
- Real-time star rating component
- Animated progress bars for match scores
- Responsive layout for all devices

### Analytics Page
- Total recommendations generated
- Total active users
- Most popular category
- Average similarity score
- Category distribution pie chart
- Rating distribution bar chart
- Trending categories area chart
- Platform overview statistics

### Admin Panel
- User management (list, search, delete)
- Recommendation history logs
- CSV data export for users and recommendations
- Search functionality
- Real-time statistics

## Tech Stack

### Backend
- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin resource sharing
- **Pandas** - Data manipulation
- **NumPy** - Numerical computing
- **Scikit-Learn** - TF-IDF vectorization and cosine similarity
- **SQLite** - Lightweight database

### Frontend
- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Data visualization charts
- **Lucide React** - Icon library

## Project Structure

```
project/
|
├── backend/
|   ├── app.py                 # Flask application with all API routes
|   ├── recommendation.py      # Content-based filtering engine
|   ├── database.py            # SQLite database operations
|   ├── recommendation.db      # SQLite database (auto-generated)
|   └── requirements.txt       # Python dependencies
|
├── src/
|   ├── App.tsx                # Main React application
|   ├── App.css                # Application styles & animations
|   ├── index.css              # Global styles & design system
|   ├── main.tsx               # Entry point
|   └── services/
|       └── api.ts             # API client
|
├── data/
|   └── recommendations.csv    # Sample dataset
|
├── .env                       # Environment variables
├── .env.example               # Environment variables template
├── package.json               # Node.js dependencies
├── vite.config.ts             # Vite configuration
├── tailwind.config.js         # Tailwind CSS configuration
├── tsconfig.json              # TypeScript configuration
└── README.md                  # This file
```

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- pip
- npm

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd ai-recommendation-engine
```

### 2. Backend Setup

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
cd backend
pip install -r requirements.txt

# Start Flask server
python app.py
```

The Flask API will start on `http://localhost:5000`

### 3. Frontend Setup

```bash
# In a new terminal, install Node.js dependencies
npm install

# Start development server
npm run dev
```

The React app will start on `http://localhost:5173`

### 4. Open in Browser

Navigate to `http://localhost:5173` to use the AI Recommendation Engine.

## API Documentation

### Get Recommendations

**Endpoint:** `POST /recommend`

**Request Body:**
```json
{
  "user_id": 1,
  "preferences": [
    {"category": "Machine Learning", "rating": 5},
    {"category": "Deep Learning", "rating": 4},
    {"category": "Data Science", "rating": 5}
  ],
  "top_n": 5
}
```

**Response:**
```json
{
  "success": true,
  "recommendations": [
    {
      "item_name": "ML Algorithms Bootcamp",
      "category": "Machine Learning",
      "similarity_score": 0.9123,
      "match_percentage": 91.23,
      "description": "Hands-on training with essential ML algorithms...",
      "rank": 1
    }
  ],
  "total": 5,
  "timestamp": "2024-01-01T00:00:00"
}
```

### Save User

**Endpoint:** `POST /save_user`

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com"
}
```

### Get Analytics

**Endpoint:** `GET /analytics`

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_recommendations": 150,
    "total_users": 25,
    "most_popular_category": "Machine Learning",
    "average_similarity_score": 0.875
  },
  "category_distribution": {"Machine Learning": 45, "Deep Learning": 30},
  "rating_distribution": {"5": 80, "4": 45, "3": 20, "2": 3, "1": 2},
  "trending_categories": [{"category": "AI", "count": 50}]
}
```

## Algorithm

The recommendation engine uses **Content-Based Filtering** with **Cosine Similarity**:

1. **User Profile Creation**: User preferences are converted into a weighted text profile based on category descriptions and ratings
2. **TF-IDF Vectorization**: Both user profile and item descriptions are converted to numerical vectors
3. **Cosine Similarity**: Measures the cosine of the angle between user vector and item vectors
4. **Ranking**: Items are ranked by similarity score and top N are returned

```
Similarity Score = cos(θ) = (A · B) / (||A|| × ||B||)
```

Where A is the user profile vector and B is an item vector.

## Database Schema

### Users Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| username | TEXT | Unique username |
| email | TEXT | Unique email |
| created_at | TIMESTAMP | Registration date |

### Preferences Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to users |
| category | TEXT | Interest category |
| rating | INTEGER | Rating (1-5) |
| created_at | TIMESTAMP | Creation date |

### Recommendations Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key to users |
| item_name | TEXT | Recommended item name |
| category | TEXT | Item category |
| similarity_score | REAL | Cosine similarity score |
| match_percentage | REAL | Match percentage |
| description | TEXT | Item description |
| rank | INTEGER | Recommendation rank |
| timestamp | TIMESTAMP | Generation date |

## Deployment

### Backend Deployment (Flask)

Using Gunicorn:

```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Using Docker:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Frontend Deployment (Static)

Build for production:

```bash
npm run build
```

The `dist/` folder will contain the static files ready for deployment to any web server or CDN.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `development` |
| `FLASK_DEBUG` | Debug mode | `True` |
| `PORT` | Flask server port | `5000` |
| `VITE_API_URL` | Backend API URL | `http://localhost:5000` |
| `SECRET_KEY` | Application secret key | Random |

## Configuration

The frontend expects the Flask API to be running. Update `VITE_API_URL` in `.env` if your backend is on a different URL.

For the backend, set `CORS` origins appropriately for production:

```python
CORS(app, origins=['https://yourdomain.com'])
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Built with passion for AI-powered recommendations.
