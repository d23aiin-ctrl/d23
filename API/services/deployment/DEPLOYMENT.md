# Deployment Guide

## Quick Start

### Local Development
```bash
cd deployment
./deploy.sh dev
```

### Production (Single Server)
```bash
cd deployment
./deploy.sh prod
```

---

## Server Setup (Ubuntu/Debian)

### 1. Install Docker
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Clone Repository
```bash
git clone https://github.com/your-repo/ohgrt-services.git
cd ohgrt-services/services
```

### 3. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

### 4. Deploy
```bash
cd deployment

# Make script executable
chmod +x deploy.sh

# Start services
./deploy.sh prod
```

---

## SSL Setup (Let's Encrypt)

### 1. Install Certbot
```bash
sudo apt install certbot -y
```

### 2. Get Certificate
```bash
# Stop nginx temporarily
docker-compose -f docker-compose.prod.yml stop nginx

# Get certificate
sudo certbot certonly --standalone -d api.ohgrt.com

# Copy certificates
sudo cp /etc/letsencrypt/live/api.ohgrt.com/fullchain.pem deployment/nginx/ssl/
sudo cp /etc/letsencrypt/live/api.ohgrt.com/privkey.pem deployment/nginx/ssl/
sudo chown $USER:$USER deployment/nginx/ssl/*
```

### 3. Enable HTTPS in nginx.conf
Uncomment the HTTPS server block in `deployment/nginx/nginx.conf`

### 4. Auto-Renewal
```bash
# Add to crontab
echo "0 0 1 * * certbot renew --quiet && docker-compose -f /path/to/docker-compose.prod.yml restart nginx" | sudo tee -a /etc/crontab
```

---

## Management Commands

```bash
# Start services
./deploy.sh dev    # Development
./deploy.sh prod   # Production

# Stop services
./deploy.sh stop

# View logs
./deploy.sh logs                    # All services
./deploy.sh logs finance-service    # Specific service

# Check status
./deploy.sh status

# Health check
./deploy.sh health

# Restart specific service
docker-compose restart finance-service

# Update and redeploy
git pull
docker-compose up --build -d
```

---

## Monitoring

### Enable Monitoring Stack
```bash
docker-compose -f docker-compose.prod.yml --profile monitoring up -d
```

Access:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin123)

---

## Scaling (Docker Swarm)

### Initialize Swarm
```bash
docker swarm init
```

### Deploy Stack
```bash
docker stack deploy -c docker-compose.prod.yml ohgrt
```

### Scale Service
```bash
# Scale finance service to 3 replicas
docker service scale ohgrt_finance-service=3
```

---

## Cloud Deployment Options

### AWS (ECS)
1. Push images to ECR
2. Create ECS cluster
3. Create task definitions
4. Create services with ALB

### DigitalOcean (App Platform)
1. Connect GitHub repo
2. Configure services
3. Deploy

### Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

---

## Troubleshooting

### Service not starting
```bash
# Check logs
docker-compose logs <service-name>

# Check container status
docker ps -a

# Restart service
docker-compose restart <service-name>
```

### Port already in use
```bash
# Find process using port
sudo lsof -i :<port>

# Kill process
sudo kill -9 <PID>
```

### Out of memory
```bash
# Check memory usage
docker stats

# Increase swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## Security Checklist

- [ ] Change default passwords
- [ ] Enable HTTPS with valid SSL
- [ ] Configure firewall (ufw)
- [ ] Set up fail2ban
- [ ] Enable rate limiting (configured in nginx)
- [ ] Regular security updates
- [ ] Backup strategy
