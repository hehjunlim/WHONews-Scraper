# Kubernetes Testing Tutorial

Complete guide to deploying and testing the Healthcare News Scraper on Kubernetes.

---

## 🎯 Prerequisites

### Required Tools

```bash
# Check kubectl
kubectl version --client

# Check if you have a Kubernetes cluster
kubectl cluster-info

# Check Minikube (for local testing)
minikube version
```

**Don't have Kubernetes?**

**Option 1: Minikube (Local Kubernetes)**
```bash
# macOS
brew install minikube

# Start Minikube
minikube start

# Verify
kubectl get nodes
```

**Option 2: Docker Desktop Kubernetes**
1. Open Docker Desktop
2. Settings → Kubernetes → Enable Kubernetes
3. Apply & Restart

**Option 3: Cloud Kubernetes**
- Google Kubernetes Engine (GKE)
- Amazon Elastic Kubernetes Service (EKS)
- Azure Kubernetes Service (AKS)

---

## 📦 Step 1: Review the CronJob Manifest

Check the existing Kubernetes configuration:

```bash
cat deploy/k8s-cronjob.yaml
```

This file defines:
- **CronJob**: Scheduled task (runs daily at 2 AM UTC)
- **ConfigMap**: Environment variables
- **PersistentVolumeClaim**: Database storage

---

## 🚀 Step 2: Deploy to Kubernetes

### Create a namespace (optional but recommended)

```bash
kubectl create namespace healthcare-news

# Set as default namespace for this session
kubectl config set-context --current --namespace=healthcare-news
```

### Deploy the CronJob

```bash
kubectl apply -f deploy/k8s-cronjob.yaml
```

**Expected output:**
```
configmap/healthcare-news-config created
persistentvolumeclaim/healthcare-news-pvc created
cronjob.batch/healthcare-news-scraper created
```

### Verify deployment

```bash
# Check CronJob
kubectl get cronjobs

# Check ConfigMap
kubectl get configmaps

# Check PersistentVolumeClaim
kubectl get pvc
```

**Expected output:**
```
NAME                       SCHEDULE    SUSPEND   ACTIVE   LAST SCHEDULE   AGE
healthcare-news-scraper    0 2 * * *   False     0        <none>          30s

NAME                      DATA   AGE
healthcare-news-config    7      30s

NAME                     STATUS   VOLUME                CAPACITY   ACCESS MODES
healthcare-news-pvc      Bound    pvc-abc123...         1Gi        RWO
```

---

## 🧪 Step 3: Test Manually (Don't Wait for Cron)

### Create a manual Job from the CronJob

```bash
kubectl create job --from=cronjob/healthcare-news-scraper test-run-1
```

### Watch the Job execute

```bash
# Watch job status
kubectl get jobs -w

# Check pods
kubectl get pods
```

**Expected output:**
```
NAME                            READY   STATUS      RESTARTS   AGE
test-run-1-abc123               0/1     Completed   0          45s
```

### View logs from the Job

```bash
# Get pod name
POD_NAME=$(kubectl get pods -l job-name=test-run-1 -o jsonpath='{.items[0].metadata.name}')

# View logs
kubectl logs $POD_NAME
```

**Expected logs:**
```
INFO: Starting healthcare news scraper...
INFO: Fetching articles from WHO News...
INFO: Found 47 total articles
INFO: Saving to database: /data/healthcare_news.db
INFO: Successfully stored 47 articles
INFO: Run completed successfully
```

---

## 📊 Step 4: Verify Data Persistence

### Check the PersistentVolume

```bash
# See the volume details
kubectl describe pvc healthcare-news-pvc
```

### Access the database

**Method 1: Run a debug pod with the same volume**

```bash
# Create a debug pod
kubectl run -it --rm debug \
  --image=python:3.12-slim \
  --restart=Never \
  --overrides='
{
  "spec": {
    "containers": [{
      "name": "debug",
      "image": "python:3.12-slim",
      "command": ["/bin/sh"],
      "stdin": true,
      "tty": true,
      "volumeMounts": [{
        "name": "data",
        "mountPath": "/data"
      }]
    }],
    "volumes": [{
      "name": "data",
      "persistentVolumeClaim": {
        "claimName": "healthcare-news-pvc"
      }
    }]
  }
}'
```

Inside the debug pod:
```bash
# Install sqlite3
apt-get update && apt-get install -y sqlite3

# Check database
ls -lh /data/
sqlite3 /data/healthcare_news.db "SELECT COUNT(*) FROM products;"

# Exit
exit
```

**Method 2: Copy database out of the volume**

```bash
# Create a temporary pod
kubectl run tmp-pod --image=busybox --restart=Never -- sleep 3600

# Mount the PVC to it (edit the pod)
kubectl patch pod tmp-pod -p '
{
  "spec": {
    "volumes": [{
      "name": "data",
      "persistentVolumeClaim": {
        "claimName": "healthcare-news-pvc"
      }
    }],
    "containers": [{
      "name": "busybox",
      "volumeMounts": [{
        "name": "data",
        "mountPath": "/data"
      }]
    }]
  }
}'

# Copy database to local machine
kubectl cp tmp-pod:/data/healthcare_news.db ./local_copy.db

# Query locally
sqlite3 local_copy.db "SELECT * FROM products LIMIT 5;"

# Cleanup
kubectl delete pod tmp-pod
```

---

## ⏰ Step 5: Test Scheduled Execution

### Check CronJob schedule

```bash
kubectl get cronjob healthcare-news-scraper -o yaml | grep schedule
```

**Output:**
```yaml
schedule: 0 2 * * *  # Runs at 2:00 AM UTC daily
```

### Modify schedule for testing (every 2 minutes)

```bash
kubectl patch cronjob healthcare-news-scraper -p '{"spec":{"schedule":"*/2 * * * *"}}'
```

### Watch for automatic job creation

```bash
kubectl get jobs -w
```

After 2 minutes, you should see:
```
NAME                                 COMPLETIONS   DURATION   AGE
healthcare-news-scraper-28498100     1/1           42s        1m
healthcare-news-scraper-28498102     1/1           38s        10s
```

### View logs from scheduled jobs

```bash
# Get the latest job
LATEST_JOB=$(kubectl get jobs --sort-by=.metadata.creationTimestamp -o jsonpath='{.items[-1].metadata.name}')

# Get pod from that job
POD_NAME=$(kubectl get pods -l job-name=$LATEST_JOB -o jsonpath='{.items[0].metadata.name}')

# View logs
kubectl logs $POD_NAME
```

### Reset schedule back to daily

```bash
kubectl patch cronjob healthcare-news-scraper -p '{"spec":{"schedule":"0 2 * * *"}}'
```

---

## 🔧 Step 6: Test Configuration Changes

### Update environment variables

Edit the ConfigMap:

```bash
kubectl edit configmap healthcare-news-config
```

Change values (e.g., SCRAPER_SEARCH_TERM):
```yaml
data:
  SCRAPER_SEARCH_TERM: "outbreak"  # Changed from ""
  SCRAPER_LIMIT: "10"              # Changed from "0"
```

### Test with new configuration

```bash
kubectl create job --from=cronjob/healthcare-news-scraper test-outbreak
```

### Verify new configuration took effect

```bash
POD_NAME=$(kubectl get pods -l job-name=test-outbreak -o jsonpath='{.items[0].metadata.name}')
kubectl logs $POD_NAME | grep "SCRAPER_SEARCH_TERM"
```

---

## 📈 Step 7: Monitor and Observe

### View all jobs from the CronJob

```bash
kubectl get jobs -l app=healthcare-news-scraper
```

### Check for failed jobs

```bash
kubectl get jobs -l app=healthcare-news-scraper --field-selector status.successful=0
```

### View job history (last 5 jobs)

```bash
kubectl get jobs --sort-by=.metadata.creationTimestamp | tail -6
```

### Set up log aggregation (optional)

**Using stern (better than kubectl logs):**

```bash
# Install stern
brew install stern

# Watch logs from all scraper jobs in real-time
stern healthcare-news-scraper
```

### Monitor resource usage

```bash
# Get resource usage for recent pods
kubectl top pods -l app=healthcare-news-scraper
```

**Expected output:**
```
NAME                                   CPU(cores)   MEMORY(bytes)
healthcare-news-scraper-28498100-abc   2m           45Mi
```

---

## 🎛️ Step 8: Advanced Testing

### Test with different Docker image

Build and push to a registry:

```bash
# Tag for your registry
docker tag garysguide-scraper-scraper:latest YOUR_REGISTRY/healthcare-news-scraper:v1.0.0

# Push to registry
docker push YOUR_REGISTRY/healthcare-news-scraper:v1.0.0
```

Update the CronJob:

```bash
kubectl set image cronjob/healthcare-news-scraper \
  scraper=YOUR_REGISTRY/healthcare-news-scraper:v1.0.0
```

### Test with resource limits

Edit the CronJob to add resource constraints:

```bash
kubectl edit cronjob healthcare-news-scraper
```

Add under `spec.jobTemplate.spec.template.spec.containers`:

```yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "500m"
```

### Test pod failure and restart behavior

Set the CronJob to fail:

```bash
kubectl patch cronjob healthcare-news-scraper -p '
{
  "spec": {
    "jobTemplate": {
      "spec": {
        "template": {
          "spec": {
            "containers": [{
              "name": "scraper",
              "env": [{
                "name": "DB_PATH",
                "value": "/read-only/test.db"
              }]
            }]
          }
        }
      }
    }
  }
}'
```

Create a test job:

```bash
kubectl create job --from=cronjob/healthcare-news-scraper test-failure
```

Check the failure:

```bash
kubectl get jobs test-failure -o yaml | grep -A 5 status
```

---

## 🧹 Step 9: Cleanup

### Delete test jobs

```bash
# Delete all jobs
kubectl delete jobs -l app=healthcare-news-scraper

# Or delete specific job
kubectl delete job test-run-1
```

### Suspend the CronJob (stops creating new jobs)

```bash
kubectl patch cronjob healthcare-news-scraper -p '{"spec":{"suspend":true}}'
```

### Resume the CronJob

```bash
kubectl patch cronjob healthcare-news-scraper -p '{"spec":{"suspend":false}}'
```

### Delete everything

```bash
# Delete CronJob, ConfigMap, and PVC
kubectl delete -f deploy/k8s-cronjob.yaml

# Or delete namespace (if you created one)
kubectl delete namespace healthcare-news
```

---

## 🐛 Troubleshooting

### Issue: CronJob not creating jobs

**Check suspend status:**
```bash
kubectl get cronjob healthcare-news-scraper -o jsonpath='{.spec.suspend}'
```

If `true`, resume it:
```bash
kubectl patch cronjob healthcare-news-scraper -p '{"spec":{"suspend":false}}'
```

### Issue: Pod stays in Pending state

**Check events:**
```bash
kubectl describe pod <pod-name>
```

Common causes:
- PVC not bound (check `kubectl get pvc`)
- Insufficient resources
- Image pull errors

### Issue: PVC won't bind

**Check storage classes:**
```bash
kubectl get storageclass
```

**For Minikube**, ensure storage provisioner is enabled:
```bash
minikube addons enable storage-provisioner
```

### Issue: Can't pull Docker image

**If using a private registry:**
```bash
# Create image pull secret
kubectl create secret docker-registry regcred \
  --docker-server=<your-registry> \
  --docker-username=<username> \
  --docker-password=<password>

# Add to CronJob spec
kubectl patch cronjob healthcare-news-scraper -p '
{
  "spec": {
    "jobTemplate": {
      "spec": {
        "template": {
          "spec": {
            "imagePullSecrets": [{"name": "regcred"}]
          }
        }
      }
    }
  }
}'
```

### Issue: Jobs accumulate and fill disk

**Set history limits** in CronJob:

```bash
kubectl patch cronjob healthcare-news-scraper -p '
{
  "spec": {
    "successfulJobsHistoryLimit": 3,
    "failedJobsHistoryLimit": 1
  }
}'
```

---

## ✅ Success Criteria

You've successfully deployed to Kubernetes when:

- [x] CronJob is created and shows in `kubectl get cronjobs`
- [x] Manual test job completes successfully
- [x] Logs show successful article scraping
- [x] Database file persists in PVC across pod restarts
- [x] Scheduled jobs run automatically at specified times
- [x] ConfigMap changes are applied to new jobs
- [x] Failed jobs are visible and debuggable

---

## 📚 Production Deployment Checklist

Before running in production:

- [ ] **Use a private Docker registry** (not local images)
- [ ] **Set resource limits** (prevent resource exhaustion)
- [ ] **Configure persistent storage** with backups
- [ ] **Set up monitoring** (Prometheus, Grafana)
- [ ] **Configure log aggregation** (ELK stack, CloudWatch)
- [ ] **Set secret management** (for API tokens)
- [ ] **Test disaster recovery** (PVC backup/restore)
- [ ] **Set up alerts** (failed jobs, disk space)
- [ ] **Document runbook** (incident response procedures)
- [ ] **Configure RBAC** (least privilege access)

---

## 🔐 Security Best Practices

### Use secrets for sensitive data

```bash
# Create secret for API token
kubectl create secret generic healthcare-news-secrets \
  --from-literal=API_TOKEN=your-secret-token

# Reference in CronJob
kubectl patch cronjob healthcare-news-scraper -p '
{
  "spec": {
    "jobTemplate": {
      "spec": {
        "template": {
          "spec": {
            "containers": [{
              "name": "scraper",
              "env": [{
                "name": "API_TOKEN",
                "valueFrom": {
                  "secretKeyRef": {
                    "name": "healthcare-news-secrets",
                    "key": "API_TOKEN"
                  }
                }
              }]
            }]
          }
        }
      }
    }
  }
}'
```

### Use network policies (if supported)

Restrict pod egress/ingress traffic.

### Run as non-root user

Update Dockerfile and CronJob to use non-root user.

---

## 💡 Pro Tips

- **Test locally with Minikube first** before deploying to cloud
- **Use namespaces** to isolate different environments (dev, staging, prod)
- **Tag Docker images with versions** (`v1.0.0`) not just `latest`
- **Set job history limits** to prevent job accumulation
- **Monitor PVC disk usage** - databases grow over time
- **Use init containers** for database schema migrations
- **Set up horizontal pod autoscaling** if scraping multiple sources
- **Use liveness/readiness probes** for long-running scrapers

---

## 📊 Monitoring Dashboard

Example Prometheus queries for monitoring:

```promql
# Job success rate
rate(kube_job_status_succeeded{job="healthcare-news-scraper"}[1h])

# Job failure rate
rate(kube_job_status_failed{job="healthcare-news-scraper"}[1h])

# Average job duration
rate(kube_job_complete_duration_seconds_sum[1h]) / 
rate(kube_job_complete_duration_seconds_count[1h])

# PVC usage
kubelet_volume_stats_used_bytes{persistentvolumeclaim="healthcare-news-pvc"}
```

---

## 🎓 Further Reading

- [Kubernetes CronJob Documentation](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
- [Kubernetes Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)

Happy deploying! 🚀
