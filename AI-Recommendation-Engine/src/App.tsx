import { useState, useEffect, useRef } from 'react';
import { API } from './services/api';
import {
  Sparkles, Star, User, TrendingUp, Activity, Users, Database,
  BarChart3, PieChart, Search, Trash2, Download, ChevronRight,
  Zap, Target, Award, Clock, Shield, Code, Cloud, Brain, Eye,
  MessageSquare, LineChart, Server, Globe, Cpu, RefreshCw, Settings, X
} from 'lucide-react';
import {
  PieChart as RePieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area
} from 'recharts';
import './App.css';

// ==================== TYPES ====================
interface Preference {
  category: string;
  rating: number;
}

interface Recommendation {
  item_name: string;
  category: string;
  similarity_score: number;
  match_percentage: number;
  description: string;
  rank: number;
}

interface UserData {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

// ==================== CONSTANTS ====================
const CATEGORIES = [
  { name: 'Artificial Intelligence', icon: Brain, color: '#00f0ff' },
  { name: 'Machine Learning', icon: Cpu, color: '#b829f7' },
  { name: 'Deep Learning', icon: Zap, color: '#ff2d95' },
  { name: 'Computer Vision', icon: Eye, color: '#00ff9d' },
  { name: 'NLP', icon: MessageSquare, color: '#ff6b35' },
  { name: 'Data Science', icon: LineChart, color: '#4d8af0' },
  { name: 'Web Development', icon: Globe, color: '#00f0ff' },
  { name: 'Cyber Security', icon: Shield, color: '#ff2d95' },
  { name: 'Cloud Computing', icon: Cloud, color: '#00ff9d' },
];

const COLORS = ['#00f0ff', '#b829f7', '#ff2d95', '#00ff9d', '#ff6b35', '#4d8af0', '#ffd700', '#ff4444', '#44ff44'];

// API status check endpoint

// ==================== CURSOR LIGHT EFFECT ====================
function CursorLight() {
  const cursorRef = useRef<HTMLDivElement>(null);
  const glowRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (cursorRef.current) {
        cursorRef.current.style.left = `${e.clientX}px`;
        cursorRef.current.style.top = `${e.clientY}px`;
      }
      if (glowRef.current) {
        glowRef.current.style.left = `${e.clientX}px`;
        glowRef.current.style.top = `${e.clientY}px`;
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <>
      <div ref={cursorRef} className="cursor-dot" />
      <div ref={glowRef} className="cursor-glow" />
    </>
  );
}

// ==================== STAR RATING COMPONENT ====================
function StarRating({ rating, onRate, interactive = true }: { rating: number; onRate?: (r: number) => void; interactive?: boolean }) {
  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          onClick={() => interactive && onRate?.(star)}
          className={`transition-all duration-200 ${interactive ? 'hover:scale-125 cursor-pointer' : 'cursor-default'}`}
          disabled={!interactive}
        >
          <Star
            size={20}
            className={star <= rating ? 'star-filled' : 'star-empty'}
            fill={star <= rating ? '#ffd700' : 'transparent'}
          />
        </button>
      ))}
    </div>
  );
}

// ==================== GLASS CARD COMPONENT ====================
function GlassCard({ children, className = '', onClick }: { children: React.ReactNode; className?: string; onClick?: () => void }) {
  return (
    <div
      className={`glass-card p-6 ${className}`}
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      {children}
    </div>
  );
}

// ==================== ANIMATED BACKGROUND ====================
function AnimatedBackground() {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden" style={{ zIndex: 0 }}>
      {/* Grid pattern */}
      <div className="absolute inset-0 grid-pattern opacity-50" />
      
      {/* Floating orbs */}
      <div className="floating-orb orb-1" />
      <div className="floating-orb orb-2" />
      <div className="floating-orb orb-3" />
      
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-[#0a0a0f] opacity-80" />
    </div>
  );
}

// ==================== MAIN APP ====================
export default function App() {
  // ---- STATE ----
  const [activeTab, setActiveTab] = useState<'recommend' | 'analytics' | 'admin'>('recommend');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [user, setUser] = useState<UserData | null>(null);
  const [preferences, setPreferences] = useState<Preference[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [apiConnected, setApiConnected] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Analytics state
  const [analytics, setAnalytics] = useState<any>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);

  // Admin state
  const [allUsers, setAllUsers] = useState<UserData[]>([]);
  const [allHistory, setAllHistory] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [adminLoading, setAdminLoading] = useState(false);

  // ---- EFFECTS ----
  useEffect(() => {
    checkAPIHealth();
  }, []);

  useEffect(() => {
    if (activeTab === 'analytics') {
      loadAnalytics();
    } else if (activeTab === 'admin') {
      loadAdminData();
    }
  }, [activeTab]);

  // ---- API FUNCTIONS ----
  const checkAPIHealth = async () => {
    try {
      await API.health();
      setApiConnected(true);
    } catch {
      setApiConnected(false);
    }
  };

  const showError = (msg: string) => {
    setError(msg);
    setTimeout(() => setError(''), 5000);
  };

  const showSuccess = (msg: string) => {
    setSuccess(msg);
    setTimeout(() => setSuccess(''), 5000);
  };

  const handleSaveUser = async () => {
    if (!username.trim() || !email.trim()) {
      showError('Please enter both username and email');
      return;
    }
    if (!email.includes('@') || !email.includes('.')) {
      showError('Please enter a valid email');
      return;
    }

    setLoading(true);
    try {
      const response = await API.saveUser(username, email);
      setUser(response.user);
      showSuccess(response.message);

      // Load existing preferences
      if (response.preferences && response.preferences.length > 0) {
        const prefs = response.preferences.map((p: any) => ({
          category: p.category,
          rating: p.rating,
        }));
        setPreferences(prefs);
      }
    } catch (err: any) {
      showError(err.message || 'Failed to save user');
    } finally {
      setLoading(false);
    }
  };

  const handleRateCategory = (category: string, rating: number) => {
    setPreferences((prev) => {
      const existing = prev.find((p) => p.category === category);
      if (existing) {
        return prev.map((p) => (p.category === category ? { ...p, rating } : p));
      }
      return [...prev, { category, rating }];
    });
  };

  const handleGetRecommendations = async () => {
    if (preferences.length === 0) {
      showError('Please rate at least one category');
      return;
    }

    setLoading(true);
    try {
      const response = await API.getRecommendations(
        user?.id || null,
        preferences,
        5
      );
      setRecommendations(response.recommendations);
      showSuccess('Recommendations generated successfully!');
    } catch (err: any) {
      showError(err.message || 'Failed to get recommendations');
    } finally {
      setLoading(false);
    }
  };

  const handleSavePreferences = async () => {
    if (!user) {
      showError('Please save your profile first');
      return;
    }
    if (preferences.length === 0) {
      showError('Please rate at least one category');
      return;
    }

    setLoading(true);
    try {
      await API.savePreferences(user.id, preferences);
      showSuccess('Preferences saved successfully!');
    } catch (err: any) {
      showError(err.message || 'Failed to save preferences');
    } finally {
      setLoading(false);
    }
  };

  const loadAnalytics = async () => {
    setAnalyticsLoading(true);
    try {
      const data = await API.getAnalytics();
      setAnalytics(data);
    } catch (err: any) {
      showError('Failed to load analytics');
    } finally {
      setAnalyticsLoading(false);
    }
  };

  const loadAdminData = async () => {
    setAdminLoading(true);
    try {
      const [usersRes, historyRes] = await Promise.all([
        API.getUsers(),
        API.getAllHistory(),
      ]);
      setAllUsers(usersRes.users);
      setAllHistory(historyRes.recommendations);
    } catch (err: any) {
      showError('Failed to load admin data');
    } finally {
      setAdminLoading(false);
    }
  };

  const handleSearchUsers = async () => {
    if (!searchQuery.trim()) {
      loadAdminData();
      return;
    }
    setAdminLoading(true);
    try {
      const res = await API.searchUsers(searchQuery);
      setAllUsers(res.users);
    } catch (err: any) {
      showError('Search failed');
    } finally {
      setAdminLoading(false);
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (!confirm('Are you sure you want to delete this user?')) return;
    try {
      await API.deleteUser(userId);
      showSuccess('User deleted');
      loadAdminData();
    } catch (err: any) {
      showError('Failed to delete user');
    }
  };

  const handleExport = async (table: string) => {
    try {
      const res = await API.exportData(table);
      const csv = convertToCSV(res.data);
      downloadCSV(csv, `${table}_export.csv`);
      showSuccess(`${table} exported successfully!`);
    } catch (err: any) {
      showError('Export failed');
    }
  };

  const convertToCSV = (data: any[]): string => {
    if (data.length === 0) return '';
    const headers = Object.keys(data[0]).join(',');
    const rows = data.map((row) =>
      Object.values(row)
        .map((v) => `"${String(v).replace(/"/g, '""')}"`)
        .join(',')
    );
    return [headers, ...rows].join('\n');
  };

  const downloadCSV = (csv: string, filename: string) => {
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
  };

  const getRatingForCategory = (category: string) => {
    const pref = preferences.find((p) => p.category === category);
    return pref ? pref.rating : 0;
  };

  // ---- RENDER ----
  return (
    <div className="min-h-screen animated-bg text-white relative">
      <CursorLight />
      <AnimatedBackground />

      {/* Notifications */}
      {error && (
        <div className="fixed top-4 right-4 z-50 glass-card border-red-500/50 bg-red-500/10 px-6 py-4 rounded-xl flex items-center gap-3">
          <X size={20} className="text-red-400" />
          <p className="text-red-200">{error}</p>
        </div>
      )}
      {success && (
        <div className="fixed top-4 right-4 z-50 glass-card border-green-500/50 bg-green-500/10 px-6 py-4 rounded-xl flex items-center gap-3">
          <Sparkles size={20} className="text-green-400" />
          <p className="text-green-200">{success}</p>
        </div>
      )}

      {/* Navigation */}
      <nav className="sticky top-0 z-40 glass-card border-b border-white/5 rounded-none">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center">
                <Brain size={22} className="text-white" />
              </div>
              <span className="text-xl font-bold gradient-text">AI Rec Engine</span>
              <span className={`ml-2 px-2 py-0.5 rounded-full text-xs font-medium ${apiConnected ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                {apiConnected ? 'API Online' : 'API Offline'}
              </span>
            </div>
            <div className="flex gap-2">
              {[
                { key: 'recommend' as const, label: 'Recommend', icon: Sparkles },
                { key: 'analytics' as const, label: 'Analytics', icon: BarChart3 },
                { key: 'admin' as const, label: 'Admin', icon: Settings },
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                    activeTab === tab.key
                      ? 'tab-active'
                      : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <tab.icon size={16} />
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <section className="mb-12 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card mb-6">
            <Zap size={16} className="text-cyan-400" />
            <span className="text-sm text-cyan-300">Powered by Cosine Similarity</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold mb-4">
            <span className="gradient-text">AI Recommendation</span>
            <br />
            <span className="text-white">Engine</span>
          </h1>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Discover personalized learning paths powered by intelligent content-based filtering.
            Rate your interests and let our algorithm find the perfect matches.
          </p>
        </section>

        {activeTab === 'recommend' && (
          <>
            {/* User Profile Section */}
            <section className="mb-12">
              <GlassCard className="max-w-2xl mx-auto">
                <div className="flex items-center gap-3 mb-6">
                  <User size={24} className="text-cyan-400" />
                  <h2 className="text-2xl font-bold">Your Profile</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Username</label>
                    <input
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder="Enter username"
                      className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400/50 focus:ring-1 focus:ring-cyan-400/50 transition-all"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Email</label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter email"
                      className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400/50 focus:ring-1 focus:ring-cyan-400/50 transition-all"
                    />
                  </div>
                </div>
                <button
                  onClick={handleSaveUser}
                  disabled={loading}
                  className="btn-primary w-full flex items-center justify-center gap-2"
                >
                  {loading ? <RefreshCw size={18} className="animate-spin" /> : <User size={18} />}
                  {user ? 'Update Profile' : 'Save Profile'}
                </button>
                {user && (
                  <p className="mt-3 text-sm text-green-400 flex items-center gap-2">
                    <Award size={14} />
                    Logged in as {user.username}
                  </p>
                )}
              </GlassCard>
            </section>

            {/* Preference Selection */}
            <section className="mb-12">
              <div className="flex items-center gap-3 mb-6">
                <Target size={24} className="text-purple-400" />
                <h2 className="text-2xl font-bold">Select Your Interests</h2>
                <span className="text-sm text-gray-400">({preferences.length} selected)</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                {CATEGORIES.map((cat) => {
                  const rating = getRatingForCategory(cat.name);
                  const isSelected = rating > 0;
                  return (
                    <GlassCard
                      key={cat.name}
                      className={`${isSelected ? 'neon-border-cyan' : ''}`}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div
                            className="w-10 h-10 rounded-lg flex items-center justify-center"
                            style={{ backgroundColor: `${cat.color}20` }}
                          >
                            <cat.icon size={20} style={{ color: cat.color }} />
                          </div>
                          <div>
                            <h3 className="font-semibold text-white">{cat.name}</h3>
                            <p className="text-xs text-gray-400">
                              {isSelected ? `Rated ${rating}/5` : 'Not rated'}
                            </p>
                          </div>
                        </div>
                      </div>
                      <StarRating
                        rating={rating}
                        onRate={(r) => handleRateCategory(cat.name, r)}
                      />
                    </GlassCard>
                  );
                })}
              </div>
              <div className="flex gap-4 justify-center">
                <button
                  onClick={handleSavePreferences}
                  disabled={loading || !user}
                  className="btn-primary flex items-center gap-2"
                  style={{ opacity: !user ? 0.5 : 1 }}
                >
                  {loading ? <RefreshCw size={18} className="animate-spin" /> : <Database size={18} />}
                  Save Preferences
                </button>
                <button
                  onClick={handleGetRecommendations}
                  disabled={loading}
                  className="btn-primary flex items-center gap-2"
                  style={{ background: 'linear-gradient(135deg, #b829f7, #ff2d95)' }}
                >
                  {loading ? <RefreshCw size={18} className="animate-spin" /> : <Sparkles size={18} />}
                  Get Recommendations
                </button>
              </div>
            </section>

            {/* Recommendations Results */}
            {recommendations.length > 0 && (
              <section className="mb-12">
                <div className="flex items-center gap-3 mb-6">
                  <Sparkles size={24} className="text-cyan-400" />
                  <h2 className="text-2xl font-bold">Your Top Recommendations</h2>
                </div>
                <div className="space-y-4">
                  {recommendations.map((rec) => (
                    <GlassCard key={rec.rank} className="pulse-glow">
                      <div className="flex flex-col md:flex-row md:items-center gap-4">
                        {/* Rank Badge */}
                        <div className="flex-shrink-0">
                          <div
                            className="w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-bold"
                            style={{
                              background: `linear-gradient(135deg, ${COLORS[rec.rank - 1]}30, ${COLORS[rec.rank - 1]}10)`,
                              border: `1px solid ${COLORS[rec.rank - 1]}50`,
                              color: COLORS[rec.rank - 1],
                            }}
                          >
                            #{rec.rank}
                          </div>
                        </div>

                        {/* Content */}
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-xl font-bold text-white">{rec.item_name}</h3>
                            <span
                              className="px-3 py-1 rounded-full text-xs font-medium"
                              style={{
                                backgroundColor: `${COLORS[CATEGORIES.findIndex((c) => c.name === rec.category) || 0]}20`,
                                color: COLORS[CATEGORIES.findIndex((c) => c.name === rec.category) || 0],
                              }}
                            >
                              {rec.category}
                            </span>
                          </div>
                          <p className="text-gray-400 text-sm mb-3">{rec.description}</p>

                          {/* Score Bar */}
                          <div className="flex items-center gap-4">
                            <div className="flex-1">
                              <div className="flex justify-between text-xs mb-1">
                                <span className="text-gray-400">Match Score</span>
                                <span className="font-semibold" style={{ color: COLORS[rec.rank - 1] }}>
                                  {rec.match_percentage}%
                                </span>
                              </div>
                              <div className="h-2 rounded-full bg-white/10 overflow-hidden">
                                <div
                                  className="h-full rounded-full transition-all duration-1000"
                                  style={{
                                    width: `${rec.match_percentage}%`,
                                    background: `linear-gradient(90deg, ${COLORS[rec.rank - 1]}, ${COLORS[(rec.rank) % COLORS.length]})`,
                                    boxShadow: `0 0 10px ${COLORS[rec.rank - 1]}50`,
                                  }}
                                />
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="text-xs text-gray-400">Similarity</div>
                              <div className="text-lg font-bold neon-text-cyan">{rec.similarity_score}</div>
                            </div>
                          </div>
                        </div>

                        {/* Arrow */}
                        <ChevronRight size={24} className="text-gray-600 hidden md:block" />
                      </div>
                    </GlassCard>
                  ))}
                </div>
              </section>
            )}
          </>
        )}

        {activeTab === 'analytics' && (
          <>
            {/* Analytics Dashboard */}
            {analyticsLoading ? (
              <div className="flex items-center justify-center py-20">
                <RefreshCw size={40} className="animate-spin text-cyan-400" />
              </div>
            ) : analytics ? (
              <>
                {/* Stats Cards */}
                <section className="mb-12">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <GlassCard>
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                          <Activity size={20} className="text-cyan-400" />
                        </div>
                        <span className="text-gray-400 text-sm">Total Recommendations</span>
                      </div>
                      <p className="text-3xl font-bold neon-text-cyan">
                        {analytics.stats?.total_recommendations || 0}
                      </p>
                    </GlassCard>

                    <GlassCard>
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                          <Users size={20} className="text-purple-400" />
                        </div>
                        <span className="text-gray-400 text-sm">Total Users</span>
                      </div>
                      <p className="text-3xl font-bold neon-text-purple">
                        {analytics.total_users || 0}
                      </p>
                    </GlassCard>

                    <GlassCard>
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 rounded-lg bg-pink-500/20 flex items-center justify-center">
                          <TrendingUp size={20} className="text-pink-400" />
                        </div>
                        <span className="text-gray-400 text-sm">Top Category</span>
                      </div>
                      <p className="text-lg font-bold neon-text-pink truncate">
                        {analytics.stats?.most_popular_category || 'N/A'}
                      </p>
                    </GlassCard>

                    <GlassCard>
                      <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                          <Target size={20} className="text-green-400" />
                        </div>
                        <span className="text-gray-400 text-sm">Avg Similarity</span>
                      </div>
                      <p className="text-3xl font-bold neon-text-green">
                        {analytics.stats?.average_similarity_score
                          ? (analytics.stats.average_similarity_score * 100).toFixed(1)
                          : 0}%
                      </p>
                    </GlassCard>
                  </div>
                </section>

                {/* Charts */}
                <section className="mb-12">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Category Distribution Pie Chart */}
                    <GlassCard>
                      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <PieChart size={18} className="text-cyan-400" />
                        Category Distribution
                      </h3>
                      <ResponsiveContainer width="100%" height={300}>
                        <RePieChart>
                          <Pie
                            data={Object.entries(analytics.category_distribution || {}).map(([name, value]) => ({
                              name,
                              value,
                            }))}
                            cx="50%"
                            cy="50%"
                            outerRadius={100}
                            dataKey="value"
                            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                          >
                            {Object.entries(analytics.category_distribution || {}).map((_, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip
                            contentStyle={{
                              backgroundColor: '#1a1a25',
                              border: '1px solid rgba(255,255,255,0.1)',
                              borderRadius: '8px',
                              color: '#fff',
                            }}
                          />
                        </RePieChart>
                      </ResponsiveContainer>
                    </GlassCard>

                    {/* Rating Distribution Bar Chart */}
                    <GlassCard>
                      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <BarChart3 size={18} className="text-purple-400" />
                        Rating Distribution
                      </h3>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart
                          data={Object.entries(analytics.rating_distribution || {}).map(([rating, count]) => ({
                            rating: `${rating} Star${Number(rating) > 1 ? 's' : ''}`,
                            count,
                          }))}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                          <XAxis dataKey="rating" stroke="#6b6b80" />
                          <YAxis stroke="#6b6b80" />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: '#1a1a25',
                              border: '1px solid rgba(255,255,255,0.1)',
                              borderRadius: '8px',
                              color: '#fff',
                            }}
                          />
                          <Bar dataKey="count" fill="#00f0ff" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </GlassCard>

                    {/* Trending Categories */}
                    <GlassCard>
                      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <TrendingUp size={18} className="text-green-400" />
                        Trending Categories
                      </h3>
                      <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={analytics.trending_categories || []}>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                          <XAxis dataKey="category" stroke="#6b6b80" />
                          <YAxis stroke="#6b6b80" />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: '#1a1a25',
                              border: '1px solid rgba(255,255,255,0.1)',
                              borderRadius: '8px',
                              color: '#fff',
                            }}
                          />
                          <Area
                            type="monotone"
                            dataKey="count"
                            stroke="#00ff9d"
                            fill="#00ff9d"
                            fillOpacity={0.2}
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    </GlassCard>

                    {/* User Preference Stats */}
                    <GlassCard>
                      <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                        <Users size={18} className="text-orange-400" />
                        Platform Overview
                      </h3>
                      <div className="space-y-4">
                        <div className="flex justify-between items-center p-3 rounded-lg bg-white/5">
                          <span className="text-gray-400">Total Preferences Saved</span>
                          <span className="text-xl font-bold text-white">{analytics.total_preferences || 0}</span>
                        </div>
                        <div className="flex justify-between items-center p-3 rounded-lg bg-white/5">
                          <span className="text-gray-400">Active Users</span>
                          <span className="text-xl font-bold text-white">{analytics.total_users || 0}</span>
                        </div>
                        <div className="flex justify-between items-center p-3 rounded-lg bg-white/5">
                          <span className="text-gray-400">Categories Available</span>
                          <span className="text-xl font-bold text-white">{CATEGORIES.length}</span>
                        </div>
                        <div className="flex justify-between items-center p-3 rounded-lg bg-white/5">
                          <span className="text-gray-400">Recommendation Accuracy</span>
                          <span className="text-xl font-bold neon-text-green">
                            {analytics.stats?.average_similarity_score
                              ? (analytics.stats.average_similarity_score * 100).toFixed(1)
                              : 0}%
                          </span>
                        </div>
                      </div>
                    </GlassCard>
                  </div>
                </section>
              </>
            ) : (
              <div className="text-center py-20 text-gray-400">
                <Activity size={48} className="mx-auto mb-4 opacity-50" />
                <p>No analytics data available</p>
              </div>
            )}
          </>
        )}

        {activeTab === 'admin' && (
          <>
            {/* Admin Panel */}
            {adminLoading ? (
              <div className="flex items-center justify-center py-20">
                <RefreshCw size={40} className="animate-spin text-cyan-400" />
              </div>
            ) : (
              <>
                {/* Search & Export */}
                <section className="mb-8">
                  <GlassCard>
                    <div className="flex flex-col md:flex-row gap-4">
                      <div className="flex-1 relative">
                        <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" />
                        <input
                          type="text"
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          onKeyPress={(e) => e.key === 'Enter' && handleSearchUsers()}
                          placeholder="Search users..."
                          className="w-full pl-12 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-400/50 transition-all"
                        />
                      </div>
                      <button
                        onClick={handleSearchUsers}
                        className="btn-primary flex items-center gap-2"
                      >
                        <Search size={18} />
                        Search
                      </button>
                      <button
                        onClick={() => handleExport('users')}
                        className="btn-primary flex items-center gap-2"
                        style={{ background: 'linear-gradient(135deg, #00ff9d, #00c774)' }}
                      >
                        <Download size={18} />
                        Export Users
                      </button>
                      <button
                        onClick={() => handleExport('recommendations')}
                        className="btn-primary flex items-center gap-2"
                        style={{ background: 'linear-gradient(135deg, #ff6b35, #ff4444)' }}
                      >
                        <Download size={18} />
                        Export History
                      </button>
                    </div>
                  </GlassCard>
                </section>

                {/* Users Table */}
                <section className="mb-8">
                  <GlassCard>
                    <div className="flex items-center gap-3 mb-4">
                      <Users size={20} className="text-cyan-400" />
                      <h3 className="text-xl font-bold">Users ({allUsers.length})</h3>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b border-white/10">
                            <th className="text-left py-3 px-4 text-sm text-gray-400 font-medium">ID</th>
                            <th className="text-left py-3 px-4 text-sm text-gray-400 font-medium">Username</th>
                            <th className="text-left py-3 px-4 text-sm text-gray-400 font-medium">Email</th>
                            <th className="text-left py-3 px-4 text-sm text-gray-400 font-medium">Joined</th>
                            <th className="text-left py-3 px-4 text-sm text-gray-400 font-medium">Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {allUsers.map((u) => (
                            <tr key={u.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                              <td className="py-3 px-4 text-sm">{u.id}</td>
                              <td className="py-3 px-4 font-medium">{u.username}</td>
                              <td className="py-3 px-4 text-sm text-gray-400">{u.email}</td>
                              <td className="py-3 px-4 text-sm text-gray-400">
                                {new Date(u.created_at).toLocaleDateString()}
                              </td>
                              <td className="py-3 px-4">
                                <button
                                  onClick={() => handleDeleteUser(u.id)}
                                  className="p-2 rounded-lg hover:bg-red-500/20 text-red-400 transition-colors"
                                >
                                  <Trash2 size={16} />
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {allUsers.length === 0 && (
                        <div className="text-center py-8 text-gray-400">No users found</div>
                      )}
                    </div>
                  </GlassCard>
                </section>

                {/* Recommendations History */}
                <section className="mb-8">
                  <GlassCard>
                    <div className="flex items-center gap-3 mb-4">
                      <Clock size={20} className="text-purple-400" />
                      <h3 className="text-xl font-bold">Recommendation History ({allHistory.length})</h3>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b border-white/10">
                            <th className="text-left py-3 px-4 text-sm text-gray-400 font-medium">ID</th>
                            <th className="text-left py-3 px-4 text-sm text-gray-400 font-medium">User ID</th>
                            <th className="text-left py-3 px-4 text-sm text-gray-400 font-medium">Item</th>
                            <th className="text-left py-3 px-4 text-sm text-gray-400 font-medium">Category</th>
                            <th className="text-left py-3 px-4 text-sm text-gray-400 font-medium">Score</th>
                            <th className="text-left py-3 px-4 text-sm text-gray-400 font-medium">Match %</th>
                            <th className="text-left py-3 px-4 text-sm text-gray-400 font-medium">Date</th>
                          </tr>
                        </thead>
                        <tbody>
                          {allHistory.slice(0, 50).map((h) => (
                            <tr key={h.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                              <td className="py-3 px-4 text-sm">{h.id}</td>
                              <td className="py-3 px-4 text-sm">{h.user_id}</td>
                              <td className="py-3 px-4 font-medium">{h.item_name}</td>
                              <td className="py-3 px-4">
                                <span
                                  className="px-2 py-1 rounded-full text-xs"
                                  style={{
                                    backgroundColor: `${COLORS[CATEGORIES.findIndex((c) => c.name === h.category) || 0]}20`,
                                    color: COLORS[CATEGORIES.findIndex((c) => c.name === h.category) || 0],
                                  }}
                                >
                                  {h.category}
                                </span>
                              </td>
                              <td className="py-3 px-4 text-sm neon-text-cyan">{h.similarity_score}</td>
                              <td className="py-3 px-4 text-sm neon-text-green">{h.match_percentage}%</td>
                              <td className="py-3 px-4 text-sm text-gray-400">
                                {new Date(h.timestamp).toLocaleDateString()}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {allHistory.length === 0 && (
                        <div className="text-center py-8 text-gray-400">No history found</div>
                      )}
                    </div>
                  </GlassCard>
                </section>
              </>
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/5 py-8 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Brain size={20} className="text-cyan-400" />
            <span className="gradient-text font-bold">AI Recommendation Engine</span>
          </div>
          <p className="text-gray-500 text-sm">
            Powered by Content-Based Filtering and Cosine Similarity
          </p>
          <div className="flex items-center justify-center gap-6 mt-4 text-sm text-gray-500">
            <span className="flex items-center gap-1"><Code size={14} /> Flask API</span>
            <span className="flex items-center gap-1"><Server size={14} /> SQLite Database</span>
            <span className="flex items-center gap-1"><Brain size={14} /> Scikit-Learn</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
