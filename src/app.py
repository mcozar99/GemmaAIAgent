
from flask import Flask, jsonify, request, abort, render_template_string
import pandas as pd
import os
from functools import wraps
from datetime import datetime
import plotly.graph_objs as go
import plotly.express as px
import json
import plotly

app = Flask(__name__)

API_KEY = os.environ.get('ACME_API_KEY', 'testkey123')  # Set a default for local dev

# Initialize call metrics CSV file
def init_call_metrics_csv():
    csv_path = os.path.join(os.path.dirname(__file__), 'call_metrics.csv')
    if not os.path.exists(csv_path):
        df = pd.DataFrame(columns=[
            'timestamp', 'mc_number', 'carrier_name', 'call_duration', 
            'load_id', 'outcome', 'sentiment', 'negotiation_rounds',
            'initial_rate', 'final_rate', 'rate_difference', 'load_accepted'
        ])
        df.to_csv(csv_path, index=False)
    return csv_path

# Initialize CSV on startup
init_call_metrics_csv()

# Dashboard HTML template with Plotly
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Acme Logistics - Inbound Carrier Sales Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f8f9fa; 
        }
        .header {
            background: linear-gradient(135deg, #007bff, #0056b3);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }
        .header h1 { margin: 0; font-size: 2.5em; }
        .header p { margin: 10px 0 0 0; opacity: 0.9; }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 4px solid #007bff;
        }
        .metric-card h3 { margin: 0; color: #333; font-size: 0.9em; text-transform: uppercase; }
        .metric-card .value { font-size: 2.5em; font-weight: bold; color: #007bff; margin: 10px 0; }
        .metric-card .change { font-size: 0.8em; color: #28a745; }
        
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
        }
        .chart-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .chart-card h3 { margin-top: 0; color: #333; }
        
        .controls {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .refresh-btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            margin-right: 10px;
        }
        .refresh-btn:hover { background: #0056b3; }
        
        .status { 
            padding: 10px; 
            border-radius: 6px; 
            margin: 10px 0; 
            display: none;
        }
        .status.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Acme Logistics</h1>
        <p>Inbound Carrier Sales Automation Dashboard</p>
    </div>
    
    <div class="controls">
        <button onclick="loadDashboard()" class="refresh-btn">🔄 Refresh Data</button>
        <button onclick="exportData()" class="refresh-btn">📊 Export CSV</button>
        <span id="lastUpdated" style="color: #666; margin-left: 20px;"></span>
    </div>
    
    <div id="status" class="status"></div>
    
    <div class="metrics-grid">
        <div class="metric-card">
            <h3>Total Calls</h3>
            <div class="value" id="totalCalls">-</div>
            <div class="change">📞 Inbound carriers</div>
        </div>
        <div class="metric-card">
            <h3>Success Rate</h3>
            <div class="value" id="successRate">-</div>
            <div class="change">✅ Load acceptance</div>
        </div>
        <div class="metric-card">
            <h3>Avg Call Duration</h3>
            <div class="value" id="avgDuration">-</div>
            <div class="change">⏱️ Per call</div>
        </div>
        <div class="metric-card">
            <h3>Loads Accepted</h3>
            <div class="value" id="loadsAccepted">-</div>
            <div class="change">🚛 Confirmed bookings</div>
        </div>
        <div class="metric-card">
            <h3>Avg Negotiations</h3>
            <div class="value" id="avgNegotiations">-</div>
            <div class="change">💬 Rounds per call</div>
        </div>
        <div class="metric-card">
            <h3>Successful Calls</h3>
            <div class="value" id="successfulCalls">-</div>
            <div class="change">📈 Completed transfers</div>
        </div>
    </div>
    
    <div class="charts-grid">
        <div class="chart-card">
            <h3>📊 Call Outcomes Distribution</h3>
            <div id="outcomesChart"></div>
        </div>
        
        <div class="chart-card">
            <h3>😊 Carrier Sentiment Analysis</h3>
            <div id="sentimentChart"></div>
        </div>
        
        <div class="chart-card">
            <h3>📅 Daily Call Volume</h3>
            <div id="dailyVolumeChart"></div>
        </div>
        
        <div class="chart-card">
            <h3>💰 Rate Negotiation Distribution</h3>
            <div id="rateNegotiationChart"></div>
        </div>
        
        <div class="chart-card">
            <h3>⏱️ Call Duration vs Load Acceptance</h3>
            <div id="durationSuccessChart"></div>
        </div>
    </div>

    <script>
        const API_KEY = 'testkey123';
        
        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.className = `status ${type}`;
            statusDiv.style.display = 'block';
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 3000);
        }
        
        async function loadDashboard() {
            try {
                showStatus('Loading dashboard data...', 'success');
                
                const response = await fetch('/dashboard/data', {
                    headers: {
                        'x-api-key': API_KEY
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                // Update metrics
                updateMetrics(data.metrics);
                
                // Update charts
                updateCharts(data.charts);
                
                // Update last updated time
                document.getElementById('lastUpdated').textContent = 
                    `Last updated: ${new Date().toLocaleTimeString()}`;
                
                showStatus('Dashboard updated successfully!', 'success');
                
            } catch (error) {
                console.error('Error loading dashboard:', error);
                showStatus(`Error loading dashboard: ${error.message}`, 'error');
            }
        }
        
        function updateMetrics(metrics) {
            document.getElementById('totalCalls').textContent = metrics.total_calls || 0;
            document.getElementById('successfulCalls').textContent = metrics.successful_calls || 0;
            document.getElementById('successRate').textContent = (metrics.success_rate || 0) + '%';
            document.getElementById('avgDuration').textContent = (metrics.avg_call_duration || 0).toFixed(1) + 's';
            document.getElementById('avgNegotiations').textContent = (metrics.avg_negotiation_rounds || 0).toFixed(1);
            document.getElementById('loadsAccepted').textContent = metrics.loads_accepted || 0;
        }
        
        function updateCharts(charts) {
            // Call Outcomes Chart
            if (charts.outcomes) {
                Plotly.newPlot('outcomesChart', charts.outcomes.data, charts.outcomes.layout, {responsive: true});
            }
            
            // Sentiment Chart
            if (charts.sentiment) {
                Plotly.newPlot('sentimentChart', charts.sentiment.data, charts.sentiment.layout, {responsive: true});
            }
            
            // Daily Volume Chart
            if (charts.daily_volume) {
                Plotly.newPlot('dailyVolumeChart', charts.daily_volume.data, charts.daily_volume.layout, {responsive: true});
            }
            
            // Rate Negotiation Chart
            if (charts.rate_negotiation) {
                Plotly.newPlot('rateNegotiationChart', charts.rate_negotiation.data, charts.rate_negotiation.layout, {responsive: true});
            }
            
            // Duration vs Success Chart
            if (charts.duration_success) {
                Plotly.newPlot('durationSuccessChart', charts.duration_success.data, charts.duration_success.layout, {responsive: true});
            }
        }
        
        async function exportData() {
            try {
                const response = await fetch('/call-metrics', {
                    headers: {
                        'x-api-key': API_KEY
                    }
                });
                const data = await response.json();
                
                // Convert to CSV
                const csv = convertToCSV(data);
                
                // Download
                const blob = new Blob([csv], { type: 'text/csv' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `call_metrics_${new Date().toISOString().split('T')[0]}.csv`;
                a.click();
                window.URL.revokeObjectURL(url);
                
                showStatus('Data exported successfully!', 'success');
            } catch (error) {
                showStatus(`Export failed: ${error.message}`, 'error');
            }
        }
        
        function convertToCSV(data) {
            if (!data.length) return '';
            
            const headers = Object.keys(data[0]);
            const csvContent = [
                headers.join(','),
                ...data.map(row => headers.map(header => JSON.stringify(row[header] || '')).join(','))
            ].join('\\n');
            
            return csvContent;
        }
        
        // Load dashboard on page load
        loadDashboard();
        
        // Auto-refresh every 2 minutes
        setInterval(loadDashboard, 120000);
    </script>
</body>
</html>
'''

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get('x-api-key')
        if not key or key != API_KEY:
            abort(401, description='Invalid or missing API key')
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@require_api_key
def home():
    return 'Hello, Flask!'

@app.route('/loads', methods=['GET'])
@require_api_key
def get_loads():
    csv_path = os.path.join(os.path.dirname(__file__), 'sample_loads.csv')
    df = pd.read_csv(csv_path)
    params = request.args
    for key, value in params.items():
        if key in df.columns:
            df = df[df[key].astype(str).str.contains(value, case=False, na=False)]
    if df.empty:
        return jsonify({'message': 'No matching records found.', 'results': ''})
    # Format all matched records as a single string
    rows = []
    for _, row in df.iterrows():
        row_str = ', '.join(f"{col}: {row[col]}" for col in df.columns)
        rows.append(row_str)
    results_str = '\n'.join(rows)
    return jsonify({'message': f'Matched {len(rows)} loads.', 'results': results_str})

@app.route('/call-metrics', methods=['POST'])
@require_api_key
def log_call_metrics():
    """Log call metrics from HappyRobot platform"""
    try:
        data = request.get_json()
        
        # Create new row for call metrics
        new_row = {
            'timestamp': datetime.now().isoformat(),
            'mc_number': data.get('mc_number', ''),
            'carrier_name': data.get('carrier_name', ''),
            'call_duration': data.get('call_duration', 0),
            'load_id': data.get('load_id', ''),
            'outcome': data.get('outcome', ''),  # successful, failed, transferred, etc.
            'sentiment': data.get('sentiment', ''),  # positive, neutral, negative
            'negotiation_rounds': data.get('negotiation_rounds', 0),
            'initial_rate': data.get('initial_rate', 0),
            'final_rate': data.get('final_rate', 0),
            'rate_difference': data.get('rate_difference', 0),
            'load_accepted': data.get('load_accepted', False)
        }
        
        # Append to CSV
        csv_path = os.path.join(os.path.dirname(__file__), 'call_metrics.csv')
        df = pd.read_csv(csv_path)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(csv_path, index=False)
        
        return jsonify({'status': 'success', 'message': 'Call metrics logged successfully'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/call-metrics', methods=['GET'])
@require_api_key
def get_call_metrics():
    """Get call metrics with optional filtering"""
    csv_path = os.path.join(os.path.dirname(__file__), 'call_metrics.csv')
    df = pd.read_csv(csv_path)
    
    # Apply filters from query parameters
    if request.args.get('outcome'):
        df = df[df['outcome'] == request.args.get('outcome')]
    if request.args.get('sentiment'):
        df = df[df['sentiment'] == request.args.get('sentiment')]
    if request.args.get('load_accepted'):
        df = df[df['load_accepted'] == (request.args.get('load_accepted').lower() == 'true')]
    
    return jsonify(df.to_dict(orient='records'))

@app.route("/transfer-sales", methods=['POST'])
@require_api_key
def transfer_sales():
    """Endpoint to handle transfer of sales"""
    data = request.get_json()
    if not 'message' in data:
        return jsonify({'status': 'error', 'message': 'Missing message field'}), 400
    # mock transfer
    return jsonify({'status': 'success', 'message': f"Sales transferred successfully: {data.get('message', '')}"})

@app.route('/dashboard')
def dashboard():
    """Render the main dashboard"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/dashboard/data')
@require_api_key
def dashboard_data():
    """Generate dashboard data and charts"""
    csv_path = os.path.join(os.path.dirname(__file__), 'call_metrics.csv')
    df = pd.read_csv(csv_path)
    
    if df.empty:
        return jsonify({
            'charts': {},
            'metrics': {
                'total_calls': 0,
                'successful_calls': 0,
                'success_rate': 0,
                'avg_call_duration': 0,
                'avg_negotiation_rounds': 0,
                'loads_accepted': 0
            }
        })
    
    # Calculate key metrics
    total_calls = len(df)
    successful_calls = len(df[df['outcome'] == 'successful'])
    success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
    avg_call_duration = df['call_duration'].mean() if 'call_duration' in df.columns else 0
    avg_negotiation_rounds = df['negotiation_rounds'].mean() if 'negotiation_rounds' in df.columns else 0
    loads_accepted = len(df[df['load_accepted'] == True])
    
    # Create charts
    charts = {}
    
    # 1. Call Outcomes Pie Chart
    outcome_counts = df['outcome'].value_counts()
    charts['outcomes'] = {
        'data': [{
            'values': outcome_counts.values.tolist(),
            'labels': outcome_counts.index.tolist(),
            'type': 'pie',
            'name': 'Call Outcomes'
        }],
        'layout': {
            'title': 'Call Outcomes Distribution',
            'height': 400
        }
    }
    
    # 2. Sentiment Analysis
    sentiment_counts = df['sentiment'].value_counts()
    charts['sentiment'] = {
        'data': [{
            'x': sentiment_counts.index.tolist(),
            'y': sentiment_counts.values.tolist(),
            'type': 'bar',
            'name': 'Sentiment',
            'marker': {'color': ['#28a745', '#ffc107', '#dc3545']}
        }],
        'layout': {
            'title': 'Carrier Sentiment Analysis',
            'xaxis': {'title': 'Sentiment'},
            'yaxis': {'title': 'Number of Calls'},
            'height': 400
        }
    }
    
    # 3. Daily Call Volume
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    daily_calls = df.groupby('date').size().reset_index(name='calls')
    charts['daily_volume'] = {
        'data': [{
            'x': daily_calls['date'].astype(str).tolist(),
            'y': daily_calls['calls'].tolist(),
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': 'Daily Calls'
        }],
        'layout': {
            'title': 'Daily Call Volume',
            'xaxis': {'title': 'Date'},
            'yaxis': {'title': 'Number of Calls'},
            'height': 400
        }
    }
    
    # 4. Rate Negotiation Analysis
    if 'rate_difference' in df.columns and not df['rate_difference'].isna().all():
        charts['rate_negotiation'] = {
            'data': [{
                'x': df['rate_difference'].tolist(),
                'type': 'histogram',
                'name': 'Rate Differences',
                'nbinsx': 20
            }],
            'layout': {
                'title': 'Rate Negotiation Distribution',
                'xaxis': {'title': 'Rate Difference ($)'},
                'yaxis': {'title': 'Frequency'},
                'height': 400
            }
        }
    
    # 5. Call Duration vs Success
    charts['duration_success'] = {
        'data': [{
            'x': df[df['load_accepted'] == True]['call_duration'].tolist(),
            'y': ['Accepted'] * len(df[df['load_accepted'] == True]),
            'type': 'box',
            'name': 'Accepted Loads'
        }, {
            'x': df[df['load_accepted'] == False]['call_duration'].tolist(),
            'y': ['Rejected'] * len(df[df['load_accepted'] == False]),
            'type': 'box',
            'name': 'Rejected Loads'
        }],
        'layout': {
            'title': 'Call Duration by Load Acceptance',
            'xaxis': {'title': 'Call Duration (seconds)'},
            'height': 400
        }
    }
    
    return jsonify({
        'charts': charts,
        'metrics': {
            'total_calls': int(total_calls),
            'successful_calls': int(successful_calls),
            'success_rate': round(success_rate, 2),
            'avg_call_duration': round(avg_call_duration, 2),
            'avg_negotiation_rounds': round(avg_negotiation_rounds, 2),
            'loads_accepted': int(loads_accepted)
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)