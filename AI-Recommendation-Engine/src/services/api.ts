/**
 * API Service for AI Recommendation Engine
 * Handles all communication between React frontend and Flask backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Generic fetch wrapper with error handling
async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(error.error || `HTTP ${response.status}`);
  }

  return response.json();
}

// API Functions
export const API = {
  // Health
  health: () => fetchAPI<{ status: string; database: string; timestamp: string }>('/health'),
  
  // Categories
  getCategories: () => fetchAPI<{ success: boolean; categories: string[]; count: number }>('/categories'),
  getTrending: () => fetchAPI<{ success: boolean; trending: Array<{ category: string; count: number }> }>('/trending'),
  
  // Users
  saveUser: (username: string, email: string) => 
    fetchAPI<{ success: boolean; user: any; preferences: any[]; message: string }>('/save_user', {
      method: 'POST',
      body: JSON.stringify({ username, email }),
    }),
  
  getUsers: () => fetchAPI<{ success: boolean; users: any[]; count: number }>('/users'),
  
  searchUsers: (query: string) => 
    fetchAPI<{ success: boolean; users: any[]; count: number }>(`/users/search?q=${encodeURIComponent(query)}`),
  
  deleteUser: (userId: number) => 
    fetchAPI<{ success: boolean; message: string }>(`/users/${userId}`, {
      method: 'DELETE',
    }),
  
  // Preferences
  getPreferences: (userId: number) => 
    fetchAPI<{ success: boolean; user_id: number; preferences: any[]; distribution: Record<string, number> }>(`/preferences/${userId}`),
  
  savePreferences: (userId: number, preferences: Array<{ category: string; rating: number }>) => 
    fetchAPI<{ success: boolean; message: string; saved_preferences: any[] }>('/preferences', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, preferences }),
    }),
  
  // Recommendations
  getRecommendations: (userId: number | null, preferences: Array<{ category: string; rating: number }>, topN: number = 5) => 
    fetchAPI<{ success: boolean; recommendations: any[]; total: number; timestamp: string }>('/recommend', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, preferences, top_n: topN }),
    }),
  
  getHistory: (userId: number) => 
    fetchAPI<{ success: boolean; user_id: number; recommendations: any[]; total: number }>(`/history/${userId}`),
  
  getAllHistory: () => 
    fetchAPI<{ success: boolean; recommendations: any[]; total: number }>('/history'),
  
  // Analytics
  getAnalytics: () => 
    fetchAPI<{
      success: boolean;
      stats: {
        total_recommendations: number;
        total_users: number;
        most_popular_category: string;
        average_similarity_score: number;
      };
      category_distribution: Record<string, number>;
      rating_distribution: Record<string, number>;
      trending_categories: Array<{ category: string; count: number }>;
      total_users: number;
      total_preferences: number;
    }>('/analytics'),
  
  // Export
  exportData: (table: string) => 
    fetchAPI<{ success: boolean; table: string; data: any[]; count: number }>(`/export/${table}`),
};

export default API;
