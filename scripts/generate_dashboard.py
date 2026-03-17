"""
DataOS — HTML Dashboard Generator

Reads data/data.db and writes outputs/dashboard.html
Open dashboard.html in any browser to view.

Usage:
    .venv/bin/python scripts/generate_dashboard.py
"""

import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "data.db"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "outputs" / "dashboard.html"


def query(conn, sql, params=()):
    conn.row_factory = sqlite3.Row
    rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def build_dashboard():
    conn = sqlite3.connect(DB_PATH)

    ga4_trend = query(conn, """
        SELECT date, sessions, total_users, new_users, page_views,
               ROUND(engagement_rate * 100, 1) as engagement_pct,
               ROUND(bounce_rate * 100, 1) as bounce_pct,
               ROUND(avg_session_duration, 0) as avg_duration_sec
        FROM ga4_daily
        WHERE sessions IS NOT NULL
        ORDER BY date ASC
        LIMIT 30
    """)

    ga4_latest = query(conn, """
        SELECT * FROM ga4_daily
        WHERE sessions IS NOT NULL
        ORDER BY date DESC LIMIT 1
    """)
    latest = ga4_latest[0] if ga4_latest else {}

    sources = query(conn, """
        SELECT source, medium, sessions, users
        FROM ga4_sources
        WHERE date = (SELECT MAX(date) FROM ga4_sources)
        ORDER BY sessions DESC
        LIMIT 10
    """)

    fx = query(conn, """
        SELECT currency, rate, date
        FROM fx_rates
        WHERE date = (SELECT MAX(date) FROM fx_rates)
        ORDER BY currency
    """)

    health = query(conn, """
        SELECT source, status, records_written, collected_at
        FROM collection_log
        ORDER BY collected_at DESC
        LIMIT 10
    """)

    conn.close()

    trend_dates = [r["date"] for r in ga4_trend]
    trend_sessions = [r["sessions"] or 0 for r in ga4_trend]
    trend_users = [r["total_users"] or 0 for r in ga4_trend]
    trend_pageviews = [r["page_views"] or 0 for r in ga4_trend]
    trend_engagement = [r["engagement_pct"] or 0 for r in ga4_trend]

    source_labels = [f"{r['source']} / {r['medium']}" for r in sources]
    source_sessions = [r["sessions"] or 0 for r in sources]

    fx_currencies = [r["currency"] for r in fx]
    fx_rates_vals = [r["rate"] for r in fx]
    fx_date = fx[0]["date"] if fx else "—"

    def fmt(val, suffix=""):
        if val is None:
            return "—"
        if isinstance(val, float):
            return f"{val:.1f}{suffix}"
        return f"{val}{suffix}"

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    latest_date = latest.get("date", "—")

    eng_rate = latest.get("engagement_rate")
    eng_display = fmt(round(eng_rate * 100, 1) if eng_rate is not None else None, "%")

    dur = latest.get("avg_session_duration")
    dur_display = fmt(round(dur / 60, 1) if dur is not None else None, "m")

    health_rows = "".join(f"""<tr>
          <td>{r['source']}</td>
          <td><span class="badge {r['status']}">{r['status']}</span></td>
          <td>{r['records_written'] if r['records_written'] is not None else '—'}</td>
          <td>{r['collected_at'][:19].replace('T', ' ') if r['collected_at'] else '—'}</td>
        </tr>""" for r in health)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AIOS Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f1117; color: #e0e0e0; padding: 24px; }}
  h1 {{ font-size: 1.4rem; font-weight: 600; color: #fff; margin-bottom: 4px; }}
  .subtitle {{ font-size: 0.8rem; color: #666; margin-bottom: 28px; }}
  h2 {{ font-size: 0.85rem; font-weight: 600; color: #aaa; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 14px; }}
  .section {{ margin-bottom: 36px; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 14px; margin-bottom: 28px; }}
  .card {{ background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 10px; padding: 18px 20px; }}
  .card .label {{ font-size: 0.72rem; color: #666; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px; }}
  .card .value {{ font-size: 1.8rem; font-weight: 700; color: #fff; }}
  .card .sub {{ font-size: 0.72rem; color: #555; margin-top: 4px; }}
  .chart-box {{ background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 10px; padding: 20px; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.82rem; }}
  th {{ text-align: left; padding: 8px 12px; font-size: 0.72rem; color: #555; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid #2a2d3a; }}
  td {{ padding: 9px 12px; border-bottom: 1px solid #1e2130; color: #ccc; }}
  tr:last-child td {{ border-bottom: none; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; }}
  .badge.success {{ background: #0d2e1a; color: #4ade80; }}
  .badge.error {{ background: #2e0d0d; color: #f87171; }}
  .badge.skipped {{ background: #1e1e0d; color: #facc15; }}
  @media (max-width: 640px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>

<h1>AIOS Dashboard</h1>
<p class="subtitle">flow-pro.com.au &nbsp;·&nbsp; Generated {generated_at}</p>

<div class="section">
  <h2>Website — {latest_date}</h2>
  <div class="cards">
    <div class="card">
      <div class="label">Sessions</div>
      <div class="value">{fmt(latest.get('sessions'))}</div>
      <div class="sub">yesterday</div>
    </div>
    <div class="card">
      <div class="label">Users</div>
      <div class="value">{fmt(latest.get('total_users'))}</div>
      <div class="sub">yesterday</div>
    </div>
    <div class="card">
      <div class="label">New Users</div>
      <div class="value">{fmt(latest.get('new_users'))}</div>
      <div class="sub">yesterday</div>
    </div>
    <div class="card">
      <div class="label">Page Views</div>
      <div class="value">{fmt(latest.get('page_views'))}</div>
      <div class="sub">yesterday</div>
    </div>
    <div class="card">
      <div class="label">Engagement</div>
      <div class="value">{eng_display}</div>
      <div class="sub">rate</div>
    </div>
    <div class="card">
      <div class="label">Avg Session</div>
      <div class="value">{dur_display}</div>
      <div class="sub">duration</div>
    </div>
  </div>
</div>

<div class="section">
  <h2>Traffic Trend</h2>
  <div class="chart-box">
    <div id="chart-trend"></div>
  </div>
</div>

<div class="section grid-2">
  <div>
    <h2>Traffic Sources</h2>
    <div class="chart-box">
      <div id="chart-sources"></div>
    </div>
  </div>
  <div>
    <h2>Engagement Rate</h2>
    <div class="chart-box">
      <div id="chart-engagement"></div>
    </div>
  </div>
</div>

<div class="section">
  <h2>FX Rates (USD base · {fx_date})</h2>
  <div class="chart-box">
    <div id="chart-fx"></div>
  </div>
</div>

<div class="section">
  <h2>Collection Log</h2>
  <div class="chart-box">
    <table>
      <thead><tr><th>Source</th><th>Status</th><th>Records</th><th>Collected At</th></tr></thead>
      <tbody>{health_rows}</tbody>
    </table>
  </div>
</div>

<script>
const grid = '#2a2d3a';
const text = '#aaa';
const base = {{
  paper_bgcolor: 'transparent',
  plot_bgcolor: 'transparent',
  font: {{ color: text, size: 11 }},
  margin: {{ t: 20, r: 10, b: 40, l: 50 }},
  xaxis: {{ gridcolor: grid, linecolor: grid, tickfont: {{ color: text }} }},
  yaxis: {{ gridcolor: grid, linecolor: grid, tickfont: {{ color: text }} }},
  legend: {{ font: {{ color: text }}, bgcolor: 'transparent' }},
}};

Plotly.newPlot('chart-trend', [
  {{ x: {json.dumps(trend_dates)}, y: {json.dumps(trend_sessions)}, name: 'Sessions', type: 'scatter', mode: 'lines+markers', line: {{ color: '#6366f1', width: 2 }}, marker: {{ size: 5 }} }},
  {{ x: {json.dumps(trend_dates)}, y: {json.dumps(trend_users)}, name: 'Users', type: 'scatter', mode: 'lines+markers', line: {{ color: '#22d3ee', width: 2 }}, marker: {{ size: 5 }} }},
  {{ x: {json.dumps(trend_dates)}, y: {json.dumps(trend_pageviews)}, name: 'Page Views', type: 'scatter', mode: 'lines+markers', line: {{ color: '#f59e0b', width: 2 }}, marker: {{ size: 5 }} }},
], {{...base, height: 280}}, {{responsive: true, displayModeBar: false}});

Plotly.newPlot('chart-sources', [
  {{ x: {json.dumps(source_sessions)}, y: {json.dumps(source_labels)}, type: 'bar', orientation: 'h', marker: {{ color: '#6366f1' }} }},
], {{...base, height: 260, margin: {{ t: 20, r: 20, b: 40, l: 140 }}}}, {{responsive: true, displayModeBar: false}});

Plotly.newPlot('chart-engagement', [
  {{ x: {json.dumps(trend_dates)}, y: {json.dumps(trend_engagement)}, name: 'Engagement %', type: 'scatter', mode: 'lines+markers', fill: 'tozeroy', line: {{ color: '#4ade80', width: 2 }}, fillcolor: 'rgba(74,222,128,0.1)' }},
], {{...base, height: 260, yaxis: {{ ...base.yaxis, ticksuffix: '%', range: [0, 100] }}}}, {{responsive: true, displayModeBar: false}});

Plotly.newPlot('chart-fx', [
  {{ x: {json.dumps(fx_currencies)}, y: {json.dumps(fx_rates_vals)}, type: 'bar',
     marker: {{ color: ['#6366f1','#22d3ee','#f59e0b','#4ade80','#f87171','#a78bfa','#fb923c'] }} }},
], {{...base, height: 240, yaxis: {{ ...base.yaxis, title: 'Rate from USD' }}}}, {{responsive: true, displayModeBar: false}});
</script>
</body>
</html>
"""

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html)
    print(f"Dashboard written to: {OUTPUT_PATH}")
    return OUTPUT_PATH


if __name__ == "__main__":
    path = build_dashboard()
    print(f"Open in browser: file://{path}")
