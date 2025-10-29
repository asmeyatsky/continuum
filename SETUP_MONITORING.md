# Monitoring & Alerting Setup Guide

Complete guide for setting up Prometheus, Grafana, and alerting for Continuum.

## Architecture

```
┌──────────────┐
│  Continuum   │──────────┐
│  Application │          │ /metrics (text format)
└──────────────┘          │
                          ▼
                    ┌──────────────┐
                    │ Prometheus   │
                    │ (scrape)     │
                    └──────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
      ┌────────┐    ┌─────────┐    ┌──────────┐
      │ Grafana│    │AlertMgr │    │Alerting  │
      │(visual)│    │(rules)  │    │Rules     │
      └────────┘    └─────────┘    └──────────┘
```

## Prometheus Configuration

### Location
- Docker: `/etc/prometheus/prometheus.yml`
- Kubernetes: ConfigMap `prometheus-config`
- File: `prometheus.yml`

### Key Configuration

```yaml
global:
  scrape_interval: 15s          # How often to scrape targets
  evaluation_interval: 15s      # How often to evaluate rules
  external_labels:
    cluster: continuum
    environment: production

alerting:
  alertmanagers:
  - static_configs:
    - targets:
      - alertmanager:9093

rule_files:
  - /etc/prometheus/alert_rules.yml

scrape_configs:
  - job_name: continuum
    static_configs:
    - targets: ['continuum:8000']
    relabel_configs:
    - source_labels: [__address__]
      target_label: instance
```

### Scrape Configuration

Add new scrape targets:

```yaml
scrape_configs:
  # Application metrics
  - job_name: continuum
    static_configs:
    - targets: ['continuum:8000']

  # Node metrics (if using node-exporter)
  - job_name: node
    static_configs:
    - targets: ['node-exporter:9100']

  # Database metrics (if using postgres-exporter)
  - job_name: postgres
    static_configs:
    - targets: ['postgres-exporter:9187']
```

## Metrics Reference

### HTTP Metrics

**Request Count**
```
metric: http_requests_total
type: Counter
labels: method, endpoint, status
example: http_requests_total{method="POST", endpoint="/api/explorations", status="200"}
```

**Request Duration**
```
metric: http_request_duration_seconds
type: Histogram
labels: method, endpoint
buckets: 0.01, 0.05, 0.1, 0.5, 1, 2, 5
example: http_request_duration_seconds_bucket{le="0.1", method="GET"}
```

**Request/Response Size**
```
metrics:
  - http_request_size_bytes
  - http_response_size_bytes
type: Histogram
labels: method, endpoint[, status]
```

### Database Metrics

```
# Query duration
metric: db_query_duration_seconds
labels: operation, table
buckets: 0.001, 0.01, 0.05, 0.1, 0.5, 1

# Query count
metric: db_queries_total
labels: operation, table, status

# Active connections
metric: db_connections_active

# Connection pool size
metric: db_connection_pool_size
```

### Cache Metrics

```
# Cache hits/misses
metrics:
  - cache_hits_total
  - cache_misses_total
  - cache_evictions_total
labels: cache_type, key_prefix

# Cache size
metric: cache_size_bytes
metric: cache_entries
```

### Business Metrics

```
# Explorations
metrics:
  - explorations_submitted_total
  - explorations_completed_total
  - exploration_duration_seconds

# Agents
metrics:
  - agent_executions_total
  - agent_execution_duration_seconds

# Knowledge graph
metrics:
  - knowledge_graph_nodes_total
  - knowledge_graph_edges_total

# Image generation
metric: images_generated_total
labels: provider
```

### System Metrics

```
# Application info
metric: application_info
labels: application, version

# Tracing
metric: tracing_spans_total
labels: service, span_name

# Errors
metric: errors_total
labels: error_type, location
```

## PromQL Query Examples

### Request Metrics

```promql
# Request rate (requests per second)
rate(http_requests_total[5m])

# Success rate
rate(http_requests_total{status=~"2.."}[5m]) / rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# P95 response time
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Average response time
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])

# Request count by endpoint
sum(rate(http_requests_total[5m])) by (endpoint)
```

### Database Metrics

```promql
# Slow queries
rate(db_query_duration_seconds_bucket{le="+Inf"}[5m]) - rate(db_query_duration_seconds_bucket{le="0.1"}[5m])

# Query error rate
rate(db_queries_total{status="failure"}[5m]) / rate(db_queries_total[5m])

# Database connection usage
db_connections_active / db_connection_pool_size
```

### Cache Metrics

```promql
# Cache hit rate
rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))

# Cache size
cache_size_bytes

# Eviction rate
rate(cache_evictions_total[5m])
```

## Grafana Setup

### Access

```
Default URL: http://localhost:3000
Username: admin
Password: admin
```

### Add Prometheus Data Source

1. Settings → Data Sources
2. Add data source → Prometheus
3. URL: http://prometheus:9090
4. Click "Save & Test"

### Create Dashboard

1. Click "+" → Create Dashboard
2. Add panel → Prometheus
3. Enter PromQL query
4. Set visualization (graph, gauge, heatmap, etc.)
5. Save dashboard

### Example Dashboard JSON

```json
{
  "dashboard": {
    "title": "Continuum Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
          }
        ]
      },
      {
        "title": "P95 Response Time",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds)"
          }
        ]
      }
    ]
  }
}
```

## Alert Rules

### Location
- File: `alert_rules.yml`
- Kubernetes: ConfigMap `prometheus-rules`

### Alert Configuration

```yaml
groups:
  - name: continuum_alerts
    interval: 30s
    rules:
      - alert: AlertName
        expr: metric > threshold
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Alert summary"
          description: "Detailed description"
```

### Example Alert Rules

```yaml
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High error rate detected"
    description: "Error rate is {{ $value | humanizePercentage }} (threshold: 5%)"

- alert: HighResponseTime
  expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High response time detected"
    description: "P95 response time is {{ $value | humanizeDuration }}"

- alert: DatabaseSlowQueries
  expr: rate(db_query_duration_seconds_bucket{le="+Inf"}[5m]) - rate(db_query_duration_seconds_bucket{le="0.1"}[5m]) > 0.1
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Slow database queries detected"
    description: "Slow query rate is {{ $value }}/s"
```

## Alertmanager Setup

### Configuration

```yaml
global:
  resolve_timeout: 5m

route:
  receiver: 'default'
  group_by: ['alertname', 'cluster']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
      repeat_interval: 5m

receivers:
  - name: 'default'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'

  - name: 'pagerduty'
    pagerduty_configs:
      - routing_key: 'YOUR_ROUTING_KEY'
```

### Slack Integration

```yaml
slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
    channel: '#continuum-alerts'
    title: 'Alert: {{ .GroupLabels.alertname }}'
    text: '{{ .CommonAnnotations.description }}'
    send_resolved: true
```

### Email Integration

```yaml
email_configs:
  - to: 'alerts@example.com'
    from: 'alertmanager@example.com'
    smarthost: 'smtp.example.com:587'
    auth_username: 'user@example.com'
    auth_password: 'password'
    headers:
      Subject: 'Alert: {{ .GroupLabels.alertname }}'
```

## Metrics Export

### Prometheus Metrics Endpoint

```bash
# Get metrics
curl http://localhost:8000/metrics

# Filter specific metric
curl http://localhost:8000/metrics | grep http_requests_total

# Export to file
curl http://localhost:8000/metrics > metrics.txt
```

### Export Formats

**Prometheus Text Format** (default)
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/health",status="200"} 12345
```

### Integration with Monitoring Systems

```bash
# Datadog
curl -X POST https://api.datadoghq.com/api/v1/series \
  -H "DD-API-KEY: YOUR_API_KEY" \
  -d @metrics.json

# New Relic
curl -X POST https://api.newrelic.com/v1/accounts/YOUR_ACCOUNT_ID/applications \
  -H "X-Api-Key: YOUR_API_KEY" \
  -d @metrics.json
```

## Performance Tuning

### Prometheus

```yaml
# Increase storage
command:
  - '--storage.tsdb.retention.size=50GB'
  - '--storage.tsdb.path=/prometheus'

# Adjust scrape settings
global:
  scrape_interval: 30s      # Less frequent for high-volume
  scrape_timeout: 10s
```

### Grafana

```yaml
# Increase panel cache
[grafana]
cache_size = 100

# Optimize queries
[auth]
disable_login_form = false
  auto_login = true
```

## Backup & Recovery

### Backup Prometheus Data

```bash
# Docker
docker cp continuum_prometheus_1:/prometheus /backup/prometheus

# Kubernetes
kubectl exec prometheus-pod -n continuum -- tar czf /tmp/prometheus.tar.gz /prometheus
kubectl cp continuum/prometheus-pod:/tmp/prometheus.tar.gz ./prometheus-backup.tar.gz
```

### Restore Prometheus Data

```bash
# Docker
docker cp /backup/prometheus continuum_prometheus_1:/

# Kubernetes
kubectl cp ./prometheus-backup.tar.gz continuum/prometheus-pod:/tmp/
kubectl exec prometheus-pod -n continuum -- tar xzf /tmp/prometheus.tar.gz -C /
```

## Troubleshooting

### Metrics Not Appearing

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check scrape status
curl http://localhost:9090/api/v1/query?query=up

# Verify metrics endpoint
curl http://continuum:8000/metrics

# Check logs
kubectl logs prometheus-pod -n continuum
```

### High Memory Usage

```bash
# Reduce retention
kubectl patch cm prometheus-config -n continuum -p \
  '{"data":{"prometheus.yml":"...--storage.tsdb.retention.time=7d..."}}'

# Reduce scrape frequency
edit prometheus.yml and increase scrape_interval
```

### Alert Not Firing

```bash
# Check rule syntax
promtool check rules /etc/prometheus/alert_rules.yml

# Verify metrics exist
curl 'http://localhost:9090/api/v1/query?query=metric_name'

# Check alert status
curl http://localhost:9090/api/v1/rules
```

## Next Steps

1. Create custom dashboards for your specific use cases
2. Configure alerting integrations (Slack, PagerDuty, etc.)
3. Set up log aggregation
4. Implement custom exporters for additional metrics
5. Configure metric retention policies
6. Set up automated backups of metrics data
