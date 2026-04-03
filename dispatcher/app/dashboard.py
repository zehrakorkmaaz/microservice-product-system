from fastapi.responses import HTMLResponse


def build_dashboard_html(stats, logs, top_endpoints, top_error_endpoints):
    rows = ""
    endpoint_rows = ""

    for item in top_endpoints:
        endpoint_rows += f"""
        <tr>
            <td>{item.get('_id', '')}</td>
            <td>{item.get('count', 0)}</td>
        </tr>
        """
    error_rows = ""

    for item in top_error_endpoints:
        error_rows += f"""
        <tr>
            <td>{item.get('_id', '')}</td>
            <td>{item.get('count', 0)}</td>
        </tr>
        """

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
        <meta http-equiv="refresh" content="5">
        <title>Dispatcher Logs Dashboard</title>
        <style>
            body {{
                font-family: 'Segoe UI', sans-serif;
                margin: 0;
                background: #f4f6f9;
                color: #333;
            }}

            .container {{
                padding: 30px;
            }}

            h1 {{
                margin-bottom: 5px;
                font-size: 32px;
            }}

            .subtitle {{
                color: #666;
                margin-bottom: 20px;
            }}

            .cards {{
                display: flex;
                gap: 20px;
                flex-wrap: wrap;
                margin: 20px 0 30px 0;
            }}

            .card {{
                background: white;
                border-radius: 12px;
                padding: 20px;
                min-width: 180px;
                flex: 1;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }}

            .card:hover {{
                transform: translateY(-4px);
                box-shadow: 0 6px 16px rgba(0,0,0,0.12);
            }}

            .card.success {{
                border-left: 6px solid #28a745;
            }}

            .card.warn {{
                border-left: 6px solid #ffc107;
            }}

            .card.error {{
                border-left: 6px solid #dc3545;
            }}

            .card.info {{
                border-left: 6px solid #007bff;
            }}

            .card h3 {{
                margin: 0;
                font-size: 14px;
                color: #666;
                font-weight: 600;
            }}

            .card p {{
                font-size: 28px;
                font-weight: bold;
                margin-top: 10px;
                margin-bottom: 0;
            }}

            .section-title {{
                margin: 25px 0 12px 0;
                font-size: 22px;
            }}

            .table-wrapper {{
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                overflow-x: auto;
                overflow-y: auto;
                max-height: 500px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                min-width: 1100px;
            }}

            th {{
                background: #343a40;
                color: white;
                position: sticky;
                top: 0;
                z-index: 1;
            }}

            th, td {{
                padding: 10px;
                font-size: 13px;
                text-align: left;
                border-bottom: 1px solid #eee;
            }}

            tr:nth-child(even) {{
                background: #f8f9fa;
            }}

            tr:hover {{
                background: #eef4ff;
            }}

            .chart-container {{
                background: white;
                margin-top: 30px;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }}

            canvas {{
                max-height: 420px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Dispatcher Logs Dashboard</h1>
            <p class="subtitle">Son istekler ve özet analiz</p>

            <div class="cards">
                <div class="card info">
                    <h3>Total Requests</h3>
                    <p>{stats["total_requests"]}</p>
                </div>

                <div class="card success">
                    <h3>Success (2xx)</h3>
                    <p>{stats["success_requests"]}</p>
                </div>

                <div class="card warn">
                    <h3>Unauthorized (401)</h3>
                    <p>{stats["unauthorized_requests"]}</p>
                </div>

                <div class="card warn">
                    <h3>Forbidden (403)</h3>
                    <p>{stats["forbidden_requests"]}</p>
                </div>

                <div class="card error">
                    <h3>Server Errors (5xx)</h3>
                    <p>{stats["server_error_requests"]}</p>
                </div>

                <div class="card info">
                    <h3>Avg Duration (ms)</h3>
                    <p>{stats["average_duration_ms"]}</p>
                </div>
            </div>

                <div class="card info">
                    <h3>Top Service</h3>
                    <p>{stats["top_service"]}</p>
                </div>

            <h2 class="section-title">Recent Logs</h2>
            <div class="table-wrapper">
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
            </div>

            <div class="chart-container">
                <h2 class="section-title">Request Distribution</h2>
                <canvas id="chart"></canvas>
            </div>

            <div class="chart-container">
                <h2 class="section-title">Service Request Distribution</h2>
                <canvas id="serviceChart"></canvas>
            </div>
            <h2 class="section-title">Top 5 Endpoints</h2>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Endpoint</th>
                            <th>Request Count</th>
                        </tr>
                     </thead>
                    <tbody>
                        {endpoint_rows}
                    </tbody>
                </table>
            </div>

            <h2 class="section-title">Top 5 Error Endpoints</h2>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Endpoint</th>
                            <th>Error Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        {error_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            const ctx = document.getElementById('chart');

            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: ['Success', '401', '403', '5xx'],
                    datasets: [{{
                        label: 'Requests',
                        data: [
                            {stats["success_requests"]},
                            {stats["unauthorized_requests"]},
                            {stats["forbidden_requests"]},
                            {stats["server_error_requests"]}
                        ],
                        backgroundColor: [
                            '#28a745',
                            '#ffc107',
                            '#fd7e14',
                            '#dc3545'
                        ],
                        borderRadius: 8
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            display: true
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});

            const serviceCtx = document.getElementById('serviceChart');

            new Chart(serviceCtx, {{
                type: 'pie',
                data: {{
                    labels: ['Auth Service', 'Product Service', 'Order Service'],
                    datasets: [{{
                        data: [
                            {stats["service_counts"]["auth_service"]},
                            {stats["service_counts"]["product_service"]},
                            {stats["service_counts"]["order_service"]}
                        ],
                        backgroundColor: [
                            '#007bff',
                            '#28a745',
                            '#ffc107'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true
                }}
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)