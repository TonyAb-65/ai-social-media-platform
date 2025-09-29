import React, { useState } from 'react';
import { 
  Calendar, 
  BarChart3, 
  Wand2, 
  MessageSquare, 
  Settings, 
  Plus,
  Search,
  Bell,
  User,
  TrendingUp,
  Zap,
  Eye,
  Heart,
  Share2,
  Clock,
  Target,
  Sparkles
} from 'lucide-react';

const ModernSocialPlatform = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showAIAssistant, setShowAIAssistant] = useState(false);

  const platforms = [
    { name: 'Instagram', color: 'bg-gradient-to-r from-purple-500 to-pink-500', connected: true },
    { name: 'Twitter', color: 'bg-blue-500', connected: true },
    { name: 'LinkedIn', color: 'bg-blue-700', connected: true },
    { name: 'Facebook', color: 'bg-blue-600', connected: false }
  ];

  const upcomingPosts = [
    {
      platform: 'Instagram',
      content: 'AI revolutionizing workplace productivity...',
      time: '2:00 PM Today',
      engagement: 'High',
      status: 'scheduled'
    },
    {
      platform: 'Twitter',
      content: 'Breaking: New developments in machine learning...',
      time: '4:30 PM Today',
      engagement: 'Very High',
      status: 'scheduled'
    },
    {
      platform: 'LinkedIn',
      content: 'Industry insights: The future of remote work...',
      time: 'Tomorrow 9:00 AM',
      engagement: 'Medium',
      status: 'draft'
    }
  ];

  const metrics = [
    { label: 'Total Reach', value: '847K', change: '+12%', icon: Eye },
    { label: 'Engagement', value: '23.4K', change: '+8%', icon: Heart },
    { label: 'Shares', value: '1.2K', change: '+15%', icon: Share2 },
    { label: 'Growth Rate', value: '4.2%', change: '+2%', icon: TrendingUp }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-gray-900">SocialAI Pro</h1>
            </div>

            {/* Search */}
            <div className="flex-1 max-w-lg mx-8">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search posts, analytics, or ask AI..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowAIAssistant(!showAIAssistant)}
                className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-lg hover:shadow-lg transition-all duration-200 flex items-center space-x-2"
              >
                <Wand2 className="w-4 h-4" />
                <span>AI Assistant</span>
              </button>
              <button className="p-2 text-gray-400 hover:text-gray-600 relative">
                <Bell className="w-5 h-5" />
                <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
              </button>
              <button className="p-2 text-gray-400 hover:text-gray-600">
                <User className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* Sidebar */}
          <aside className="w-64 flex-shrink-0">
            <nav className="space-y-2">
              {[
                { id: 'dashboard', icon: BarChart3, label: 'Dashboard' },
                { id: 'calendar', icon: Calendar, label: 'Content Calendar' },
                { id: 'create', icon: Wand2, label: 'AI Studio' },
                { id: 'analytics', icon: TrendingUp, label: 'Analytics' },
                { id: 'messages', icon: MessageSquare, label: 'Messages' },
                { id: 'settings', icon: Settings, label: 'Settings' }
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 text-left rounded-lg transition-colors ${
                    activeTab === item.id
                      ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-500'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </button>
              ))}
            </nav>

            {/* Platform Status */}
            <div className="mt-8 p-4 bg-white rounded-lg border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-3">Connected Platforms</h3>
              <div className="space-y-2">
                {platforms.map((platform) => (
                  <div key={platform.name} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className={`w-3 h-3 rounded-full ${platform.color}`}></div>
                      <span className="text-sm text-gray-700">{platform.name}</span>
                    </div>
                    <div className={`w-2 h-2 rounded-full ${platform.connected ? 'bg-green-400' : 'bg-red-400'}`}></div>
                  </div>
                ))}
              </div>
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1">
            {/* AI Assistant Popup */}
            {showAIAssistant && (
              <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
                <div className="bg-white rounded-2xl p-6 max-w-md w-full mx-4 max-h-96 overflow-y-auto">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">AI Assistant</h3>
                    <button 
                      onClick={() => setShowAIAssistant(false)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      x
                    </button>
                  </div>
                  <div className="space-y-4">
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <p className="text-sm text-blue-800">Hi! I can help you create content, analyze performance, or optimize your posting schedule. What would you like to do?</p>
                    </div>
                    <div className="space-y-2">
                      <button className="w-full text-left p-3 hover:bg-gray-50 rounded-lg border border-gray-200">
                        <div className="font-medium text-gray-900">Generate content ideas</div>
                        <div className="text-sm text-gray-500">Get AI-powered post suggestions</div>
                      </button>
                      <button className="w-full text-left p-3 hover:bg-gray-50 rounded-lg border border-gray-200">
                        <div className="font-medium text-gray-900">Analyze best posting times</div>
                        <div className="text-sm text-gray-500">Optimize your schedule</div>
                      </button>
                      <button className="w-full text-left p-3 hover:bg-gray-50 rounded-lg border border-gray-200">
                        <div className="font-medium text-gray-900">Create campaign strategy</div>
                        <div className="text-sm text-gray-500">Plan your next campaign</div>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Dashboard Content */}
            {activeTab === 'dashboard' && (
              <div className="space-y-8">
                {/* Hero Section */}
                <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 rounded-2xl p-8 text-white">
                  <div className="max-w-3xl">
                    <h1 className="text-3xl font-bold mb-2">Welcome back, Alex!</h1>
                    <p className="text-blue-100 mb-6">Your content is performing 23% better this week. Ready to create more engaging posts?</p>
                    <div className="flex space-x-4">
                      <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:shadow-lg transition-shadow flex items-center space-x-2">
                        <Plus className="w-4 h-4" />
                        <span>Create Post</span>
                      </button>
                      <button className="border border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:bg-opacity-10 transition-colors flex items-center space-x-2">
                        <Zap className="w-4 h-4" />
                        <span>AI Optimize</span>
                      </button>
                    </div>
                  </div>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  {metrics.map((metric, index) => (
                    <div key={index} className="bg-white p-6 rounded-xl border border-gray-200 hover:shadow-lg transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <div className="p-2 bg-blue-50 rounded-lg">
                          <metric.icon className="w-5 h-5 text-blue-600" />
                        </div>
                        <span className="text-sm font-medium text-green-600">{metric.change}</span>
                      </div>
                      <div className="text-2xl font-bold text-gray-900 mb-1">{metric.value}</div>
                      <div className="text-sm text-gray-500">{metric.label}</div>
                    </div>
                  ))}
                </div>

                {/* Two Column Layout */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                  {/* Upcoming Posts */}
                  <div className="lg:col-span-2">
                    <div className="bg-white rounded-xl border border-gray-200 p-6">
                      <div className="flex items-center justify-between mb-6">
                        <h3 className="text-lg font-semibold text-gray-900">Upcoming Posts</h3>
                        <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">View all</button>
                      </div>
                      <div className="space-y-4">
                        {upcomingPosts.map((post, index) => (
                          <div key={index} className="border border-gray-100 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center space-x-2 mb-2">
                                  <div className={`w-3 h-3 rounded-full ${platforms.find(p => p.name === post.platform)?.color}`}></div>
                                  <span className="text-sm font-medium text-gray-900">{post.platform}</span>
                                  <span className={`px-2 py-1 text-xs rounded-full ${
                                    post.status === 'scheduled' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                                  }`}>
                                    {post.status}
                                  </span>
                                </div>
                                <p className="text-gray-700 mb-2">{post.content}</p>
                                <div className="flex items-center space-x-4 text-sm text-gray-500">
                                  <div className="flex items-center space-x-1">
                                    <Clock className="w-4 h-4" />
                                    <span>{post.time}</span>
                                  </div>
                                  <div className="flex items-center space-x-1">
                                    <Target className="w-4 h-4" />
                                    <span>{post.engagement} predicted</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Quick Actions */}
                  <div className="space-y-6">
                    <div className="bg-white rounded-xl border border-gray-200 p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
                      <div className="space-y-3">
                        <button className="w-full flex items-center space-x-3 p-3 text-left hover:bg-gray-50 rounded-lg transition-colors">
                          <div className="p-2 bg-purple-50 rounded-lg">
                            <Wand2 className="w-4 h-4 text-purple-600" />
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">AI Content Generator</div>
                            <div className="text-sm text-gray-500">Create posts instantly</div>
                          </div>
                        </button>
                        <button className="w-full flex items-center space-x-3 p-3 text-left hover:bg-gray-50 rounded-lg transition-colors">
                          <div className="p-2 bg-green-50 rounded-lg">
                            <BarChart3 className="w-4 h-4 text-green-600" />
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">Performance Report</div>
                            <div className="text-sm text-gray-500">Weekly analytics</div>
                          </div>
                        </button>
                        <button className="w-full flex items-center space-x-3 p-3 text-left hover:bg-gray-50 rounded-lg transition-colors">
                          <div className="p-2 bg-blue-50 rounded-lg">
                            <Calendar className="w-4 h-4 text-blue-600" />
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">Schedule Campaign</div>
                            <div className="text-sm text-gray-500">Plan ahead</div>
                          </div>
                        </button>
                      </div>
                    </div>

                    {/* AI Insights */}
                    <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl border border-purple-200 p-6">
                      <div className="flex items-center space-x-2 mb-4">
                        <Sparkles className="w-5 h-5 text-purple-600" />
                        <h3 className="text-lg font-semibold text-gray-900">AI Insights</h3>
                      </div>
                      <div className="space-y-3">
                        <div className="bg-white p-3 rounded-lg">
                          <p className="text-sm text-gray-700">Your Tuesday posts get 2.3x more engagement. Consider scheduling more content on Tuesdays.</p>
                        </div>
                        <div className="bg-white p-3 rounded-lg">
                          <p className="text-sm text-gray-700">Video content performs 45% better than images on your Instagram account.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
};

export default ModernSocialPlatform;
