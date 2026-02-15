# 🔧 Fix Production 502 Bad Gateway Error

## Problem

**Error**: `502 Bad Gateway` on https://d23.ai
**Cause**: Nginx is running but the Next.js application is NOT running

## Diagnosis

The 502 error means:
- ✅ Nginx web server is running
- ✅ Domain is resolving correctly
- ❌ Next.js application (upstream) is NOT running or crashed

## Solution Steps

### Step 1: SSH into Production Server

```bash
# Replace with your actual server details
ssh user@your-production-server-ip

# Or if you have an alias
ssh production
```

### Step 2: Check if Next.js App is Running

**If using PM2 (most common):**
```bash
pm2 list
# Should show your Next.js app

# Check specific app status
pm2 show d23web  # or whatever your app name is
```

**If using systemd:**
```bash
sudo systemctl status d23web
# or
sudo systemctl status next-js
```

**If using Docker:**
```bash
docker ps -a | grep d23web
```

**Manual check - find Node processes:**
```bash
ps aux | grep next
# or
ps aux | grep node
```

### Step 3: Check Application Logs

**PM2 logs:**
```bash
pm2 logs d23web --lines 100
# or
pm2 logs --lines 50
```

**Systemd logs:**
```bash
sudo journalctl -u d23web -n 100 --no-pager
```

**Application logs:**
```bash
# Check where your logs are stored
tail -f /var/log/d23web/error.log
# or
tail -f ~/d23web/logs/error.log
```

### Step 4: Restart the Application

**Option A: Using PM2 (Recommended)**
```bash
# If app exists but stopped
pm2 restart d23web

# If app doesn't exist in PM2 list
cd /path/to/D23Web
pm2 start npm --name "d23web" -- start

# Save PM2 config
pm2 save
```

**Option B: Using systemd**
```bash
sudo systemctl restart d23web
sudo systemctl status d23web
```

**Option C: Manual Restart**
```bash
# Navigate to app directory
cd /path/to/D23Web

# Build (if needed)
npm run build

# Start
npm start
# or with PM2
pm2 start npm --name "d23web" -- start
```

### Step 5: Verify Nginx Configuration

```bash
# Check nginx config
sudo nginx -t

# Check what port nginx is proxying to
sudo cat /etc/nginx/sites-available/d23.ai
# or
sudo cat /etc/nginx/conf.d/d23.ai.conf

# Common setup: nginx proxies to localhost:3000
# Make sure Next.js is running on the same port
```

### Step 6: Check Port is Listening

```bash
# Check if app is listening on expected port (usually 3000)
sudo lsof -i:3000
# or
sudo netstat -tulpn | grep :3000
# or
sudo ss -tulpn | grep :3000
```

### Step 7: Restart Nginx (if needed)

```bash
# Test config first
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
# or
sudo systemctl restart nginx
```

## Common Issues and Fixes

### Issue 1: App Crashed Due to Memory

**Check memory:**
```bash
free -h
```

**Solution:** Increase memory or optimize app
```bash
# Start with increased memory
pm2 delete d23web
pm2 start npm --name "d23web" --max-memory-restart 500M -- start
pm2 save
```

### Issue 2: Port Already in Use

```bash
# Find what's using the port
sudo lsof -i:3000

# Kill the process
sudo kill -9 <PID>

# Restart app
pm2 restart d23web
```

### Issue 3: Environment Variables Missing

```bash
# Check .env file exists
cd /path/to/D23Web
ls -la .env*

# Set environment variables for PM2
pm2 start npm --name "d23web" --env production -- start
```

### Issue 4: Build Files Missing

```bash
cd /path/to/D23Web

# Rebuild
npm run build

# Check .next folder exists
ls -la .next/

# Restart
pm2 restart d23web
```

## Quick Fix Script

Create this script on your server:

```bash
#!/bin/bash
# fix-d23web.sh

echo "🔍 Checking D23Web status..."

# Navigate to app directory
cd /path/to/D23Web || exit

echo "📦 Installing dependencies..."
npm install

echo "🏗️  Building application..."
npm run build

echo "🔄 Restarting with PM2..."
pm2 delete d23web || true
pm2 start npm --name "d23web" -- start
pm2 save

echo "✅ D23Web restarted"
echo "📊 Current status:"
pm2 list
pm2 logs d23web --lines 20
```

Make it executable:
```bash
chmod +x fix-d23web.sh
./fix-d23web.sh
```

## Typical PM2 Setup for D23Web

```bash
# On production server
cd /path/to/D23Web

# Build
npm run build

# Start with PM2
pm2 start npm --name "d23web" -- start

# Or with custom port
PORT=3000 pm2 start npm --name "d23web" -- start

# Enable auto-restart on crash
pm2 startup
pm2 save

# Monitor
pm2 monit
```

## Nginx Configuration Example

Your nginx config should look like this:

```nginx
# /etc/nginx/sites-available/d23.ai

server {
    listen 80;
    server_name d23.ai www.d23.ai;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name d23.ai www.d23.ai;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/d23.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/d23.ai/privkey.pem;

    # Proxy to Next.js app
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Verification

After fixing, verify:

```bash
# 1. Check PM2 status
pm2 list
# Should show: d23web | online

# 2. Check app is listening
curl http://localhost:3000
# Should return HTML

# 3. Check nginx
sudo nginx -t
sudo systemctl status nginx

# 4. Test from outside
curl https://d23.ai
# Should return HTML (no 502)
```

## Prevention - Auto Restart

**Enable PM2 auto-restart:**
```bash
pm2 start npm --name "d23web" --exp-backoff-restart-delay=100 -- start
pm2 save
```

**Enable PM2 on server reboot:**
```bash
pm2 startup
# Follow the command it shows
pm2 save
```

## Still Not Working?

### Check Server Resources

```bash
# Check disk space
df -h

# Check memory
free -h

# Check CPU
top

# Check processes
ps aux | grep node
```

### Check Application Errors

```bash
# View real-time logs
pm2 logs d23web --lines 100

# Check for port conflicts
sudo lsof -i:3000

# Check DNS resolution
nslookup d23.ai

# Test nginx proxy
curl -I http://localhost:3000
```

## Emergency Contacts

If the issue persists, you may need to:

1. **Check your hosting provider dashboard** (DigitalOcean, AWS, etc.)
2. **Verify server is running** (not stopped or suspended)
3. **Check firewall rules** (port 3000 might be blocked)
4. **Review recent deployments** (rollback if needed)
5. **Contact your DevOps team** or hosting support

## Summary

**Most Common Fix:**
```bash
ssh your-production-server
cd /path/to/D23Web
pm2 restart d23web
# or
pm2 start npm --name "d23web" -- start
```

**If app doesn't exist:**
```bash
cd /path/to/D23Web
npm install
npm run build
pm2 start npm --name "d23web" -- start
pm2 save
```

**Check it worked:**
```bash
pm2 list
curl http://localhost:3000
# Then visit https://d23.ai in browser
```
