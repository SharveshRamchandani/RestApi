# Runbook: Production Operations

## Deployment (Kubernetes)
1. **Apply Secrets**:
   ```bash
   kubectl apply -f infra/k8s/secrets.yaml
   ```
   *Note: Edit secrets.yaml with real credentials first.*

2. **Deploy Dependencies** (if not managed):
   ```bash
   kubectl apply -f infra/k8s/dependencies.yaml
   ```

3. **Deploy App**:
   ```bash
   kubectl apply -f infra/k8s/api.yaml
   kubectl apply -f infra/k8s/worker.yaml
   ```

## Monitoring
- **Prometheus Metrics**:
  - API: `http://<API_IP>/metrics`
  - Worker: `http://<WORKER_IP>:9090` (Port forwarded)
- **Logs**:
  - JSON usage via `kubectl logs -f deployment/n8n-pop-api`

## OpenSearch Dashboard
- Access at `http://localhost:5601` (if port forwarded from pod).
- Default credentials: `admin / StrongPassword123!`

## Disaster Recovery
- **Database Backups**:
  - Run `pg_dump` daily.
- **Failover**:
  - Workers satisfy idempotency; safe to restart.
