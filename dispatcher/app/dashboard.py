from fastapi.responses import HTMLResponse


def build_dashboard_html(stats, logs):
    rows = ""

    for log in logs:
        rows += f"""
        <tr>
            <td>{log.get('timestamp', '')}</td>
            <td>{log.get('method', '')}</td>
            <td>{log.get('path', '')}</td>
            <td>{log.get('status_code', '')}</td>
            <td>{log.get('username', '')}</td>
            <td>{log.get('role', '')}</td>
            <td>{log.get('target_service', '')}</td>
            <td>{log.get('duration_ms', '')}</td>
            <td>{log.get('error_message', '')}</td>
        </tr>
        """

    html = f"""
    <html>
    <head>
        <title>Dispatcher Logs Dashboard</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 30px;
                background: #f7f7f7;
                color: #222;
            }}
            h1 {{
                margin-bottom: 10px;
            }}
            .cards {{
                display: flex;
                gap: 16px;
                flex-wrap: wrap;
                margin-bottom: 25px;
            }}
            .card {{
                background: white;
                border-radius: 10px;
                padding: 16px;
                min-width: 180px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }}
            .card h3 {{
                margin: 0 0 8px 0;
                font-size: 16px;
            }}
            .card p {{
                margin: 0;
                font-size: 24px;
                font-weight: bold;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: left;
                font-size: 14px;
            }}
            th {{
                background: #efefef;
            }}
            .section-title {{
                margin: 25px 0 10px 0;
            }}
        </style>
    </head>
    <body>
        <h1>Dispatcher Logs Dashboard</h1>
        <p>Son istekler ve özet analiz</p>

        <div class="cards">
            <div class="card">
                <h3>Total Requests</h3>
                <p>{stats["total_requests"]}</p>
            </div>
            <div class="card">
                <h3>Success (2xx)</h3>
                <p>{stats["success_requests"]}</p>
            </div>
            <div class="card">
                <h3>Unauthorized (401)</h3>
                <p>{stats["unauthorized_requests"]}</p>
            </div>
            <div class="card">
                <h3>Forbidden (403)</h3>
                <p>{stats["forbidden_requests"]}</p>
            </div>
            <div class="card">
                <h3>Server Errors (5xx)</h3>
                <p>{stats["server_error_requests"]}</p>
            </div>
            <div class="card">
                <h3>Avg Duration (ms)</h3>
                <p>{stats["average_duration_ms"]}</p>
            </div>
        </div>

        <h2 class="section-title">Recent Logs</h2>
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Method</th>
                    <th>Path</th>
                    <th>Status</th>
                    <th>User</th>
                    <th>Role</th>
                    <th>Service</th>
                    <th>Duration (ms)</th>
                    <th>Error</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </body>
    </html>
    """
    return HTMLResponse(content=html)