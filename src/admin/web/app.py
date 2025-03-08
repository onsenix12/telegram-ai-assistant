# src/admin/web/app.py content
from flask import Flask, jsonify, request, render_template_string
from src.admin.dashboard import Dashboard
from src.admin.system_monitor import SystemMonitor

app = Flask(__name__)

# Initialize components
dashboard = Dashboard()
system_monitor = SystemMonitor()

@app.route('/')
def index():
    """Render admin dashboard."""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Learning Assistant Admin</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .card {
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 20px;
            }
            h1, h2 {
                color: #333;
            }
            .stat {
                display: inline-block;
                background-color: #f0f0f0;
                border-radius: 5px;
                padding: 15px;
                margin: 10px;
                min-width: 150px;
                text-align: center;
            }
            .stat-value {
                font-size: 24px;
                font-weight: bold;
                margin: 5px 0;
            }
            .stat-label {
                font-size: 14px;
                color: #666;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 10px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #f0f0f0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AI Learning Assistant Admin Dashboard</h1>
            
            <div class="card">
                <h2>System Health</h2>
                <div class="stats" id="system-health">Loading...</div>
            </div>
            
            <div class="card">
                <h2>Usage Statistics</h2>
                <div class="stats" id="usage-stats">Loading...</div>
            </div>
            
            <div class="card">
                <h2>Recent Conversations</h2>
                <div id="recent-conversations">Loading...</div>
            </div>
        </div>
        
        <script>
            // Fetch system health
            fetch('/api/system/health')
                .then(response => response.json())
                .then(data => {
                    const systemHealth = document.getElementById('system-health');
                    systemHealth.innerHTML = `
                        <div class="stat">
                            <div class="stat-value">${data.cpu.usage_percent}%</div>
                            <div class="stat-label">CPU Usage</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">${data.memory.usage_percent}%</div>
                            <div class="stat-label">Memory Usage</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">${data.disk.usage_percent}%</div>
                            <div class="stat-label">Disk Usage</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">${data.redis.status}</div>
                            <div class="stat-label">Redis Status</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">${data.postgres.status}</div>
                            <div class="stat-label">Postgres Status</div>
                        </div>
                    `;
                });
            
            // Fetch usage statistics
            fetch('/api/dashboard/stats')
                .then(response => response.json())
                .then(data => {
                    const usageStats = document.getElementById('usage-stats');
                    usageStats.innerHTML = `
                        <div class="stat">
                            <div class="stat-value">${data.message_count}</div>
                            <div class="stat-label">Total Messages</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">${data.user_count}</div>
                            <div class="stat-label">Total Users</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">${data.conversation_count}</div>
                            <div class="stat-label">Conversations</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">${data.active_users}</div>
                            <div class="stat-label">Active Users</div>
                        </div>
                    `;
                });
            
            // Fetch recent conversations
            fetch('/api/dashboard/conversations')
                .then(response => response.json())
                .then(data => {
                    const recentConversations = document.getElementById('recent-conversations');
                    if (data.length === 0) {
                        recentConversations.innerHTML = '<p>No conversations found.</p>';
                        return;
                    }
                    
                    let html = '<table>';
                    html += '<tr><th>User ID</th><th>Timestamp</th><th>Messages</th></tr>';
                    
                    data.forEach(conversation => {
                        html += `<tr>
                            <td>${conversation.user_id}</td>
                            <td>${conversation.timestamp}</td>
                            <td>${conversation.messages.length} messages</td>
                        </tr>`;
                    });
                    
                    html += '</table>';
                    recentConversations.innerHTML = html;
                });
        </script>
    </body>
    </html>
    ''')

@app.route('/api/system/health')
def system_health():
    """API endpoint for system health."""
    return jsonify(system_monitor.collect_system_metrics())

@app.route('/api/system/info')
def system_info():
    """API endpoint for system information."""
    return jsonify(system_monitor.get_system_info())

@app.route('/api/system/history')
def system_history():
    """API endpoint for performance history."""
    metric_type = request.args.get('metric')
    return jsonify(system_monitor.get_performance_history(metric_type))

@app.route('/api/dashboard/stats')
def dashboard_stats():
    """API endpoint for usage statistics."""
    return jsonify(dashboard.get_usage_statistics())

@app.route('/api/dashboard/conversations')
def recent_conversations():
    """API endpoint for recent conversations."""
    limit = request.args.get('limit', default=10, type=int)
    return jsonify(dashboard.get_recent_conversations(limit))

@app.route('/api/dashboard/search')
def search_conversations():
    """API endpoint for searching conversations."""
    query = request.args.get('q', default='', type=str)
    return jsonify(dashboard.search_conversations(query))

def start_admin_server():
    """Start the admin server."""
    app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    start_admin_server()