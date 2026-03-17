# Data Access Reference

> Load this file when running SQL queries or working with the data pipeline.
> Database: `data/data.db` (SQLite) | Updated daily at 6:00 AM

---

## SQLite Data Warehouse

**Location:** `data/data.db`

**Connect in Python:**
```python
import sqlite3
conn = sqlite3.connect("data/data.db")
conn.row_factory = sqlite3.Row
```

**Run a quick query from terminal:**
```bash
.venv/bin/python -c "
import sqlite3
conn = sqlite3.connect('data/data.db')
conn.row_factory = sqlite3.Row
rows = conn.execute('SELECT * FROM ga4_daily ORDER BY date DESC LIMIT 5').fetchall()
for r in rows: print(dict(r))
"
```

---

## Connected Data Sources

| Source | Table(s) | Script | What it tracks |
|--------|----------|--------|----------------|
| FX Rates | `fx_rates` | `scripts/collect_fx_rates.py` | Daily USD exchange rates (7 currencies) |
| Google Analytics | `ga4_daily`, `ga4_sources` | `scripts/collect_google_analytics.py` | Website traffic for flow-pro.com.au |

---

## Table Schemas

### `fx_rates`
Daily foreign exchange rates from the Frankfurter API (European Central Bank data).

| Column | Type | Description |
|--------|------|-------------|
| `date` | TEXT | Rate date (YYYY-MM-DD) — primary key with currency |
| `currency` | TEXT | Currency code (AUD, GBP, EUR, etc.) |
| `rate` | REAL | Exchange rate from USD |
| `base` | TEXT | Always "USD" |
| `collected_at` | TEXT | UTC timestamp of collection |

### `ga4_daily`
Daily website traffic snapshot for flow-pro.com.au from Google Analytics 4.

| Column | Type | Description |
|--------|------|-------------|
| `date` | TEXT | Date of traffic (YYYY-MM-DD) — primary key |
| `sessions` | INTEGER | Total sessions |
| `total_users` | INTEGER | Total unique users |
| `new_users` | INTEGER | First-time visitors |
| `page_views` | INTEGER | Total page views |
| `avg_session_duration` | REAL | Average session duration in seconds |
| `bounce_rate` | REAL | Bounce rate (0–1 scale) |
| `engagement_rate` | REAL | Engagement rate (0–1 scale) |
| `collected_at` | TEXT | UTC timestamp of collection |

### `ga4_sources`
Traffic source breakdown — where visitors came from each day.

| Column | Type | Description |
|--------|------|-------------|
| `date` | TEXT | Date (YYYY-MM-DD) — primary key with source+medium |
| `source` | TEXT | Traffic source (google, direct, linkedin, etc.) |
| `medium` | TEXT | Medium (organic, cpc, referral, etc.) |
| `sessions` | INTEGER | Sessions from this source |
| `users` | INTEGER | Users from this source |

### `collection_log`
Internal log of every collection run.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Auto-increment ID |
| `collected_at` | TEXT | UTC timestamp |
| `source` | TEXT | Collector name |
| `status` | TEXT | success / skipped / error / exception |
| `reason` | TEXT | Error message if failed |
| `records_written` | INTEGER | Records saved to DB |

---

## Common Queries

**Latest website traffic:**
```sql
SELECT date, sessions, total_users, new_users, page_views,
       ROUND(engagement_rate * 100, 1) as engagement_pct
FROM ga4_daily
ORDER BY date DESC
LIMIT 7;
```

**Traffic trend last 30 days:**
```sql
SELECT date, sessions, total_users
FROM ga4_daily
WHERE date >= date('now', '-30 days')
ORDER BY date;
```

**Top traffic sources (latest day):**
```sql
SELECT source, medium, sessions, users
FROM ga4_sources
WHERE date = (SELECT MAX(date) FROM ga4_sources)
ORDER BY sessions DESC
LIMIT 10;
```

**Current FX rates (AUD focused):**
```sql
SELECT currency, rate, date
FROM fx_rates
WHERE date = (SELECT MAX(date) FROM fx_rates)
ORDER BY currency;
```

**Collection health check:**
```sql
SELECT source, status, records_written, collected_at
FROM collection_log
ORDER BY collected_at DESC
LIMIT 10;
```

---

## Data Collection

**Run all collectors:**
```bash
.venv/bin/python scripts/collect.py
```

**Run specific source:**
```bash
.venv/bin/python scripts/collect.py --sources google_analytics
.venv/bin/python scripts/collect.py --sources fx_rates
```

**Regenerate key-metrics.md only:**
```bash
.venv/bin/python scripts/generate_metrics.py
```

**Check collection log:**
```bash
cat data/collect.log
```

**Schedule:** Runs automatically at 6:00 AM daily via macOS launchd (`config/com.aios.data-collect.plist`).
