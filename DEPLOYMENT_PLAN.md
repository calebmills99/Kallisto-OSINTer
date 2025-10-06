# Guardr Production Deployment Plan - DigitalOcean

## Current Architecture
- **Backend:** Flask API (guardr_api.py) running locally on port 5000
- **Frontend:** Next.js app running locally on port 3002
- **Domain:** guardr.app (owned)
- **GitHub Student Pack:** $200 DigitalOcean credit available

---

## Target Architecture

### Backend: DigitalOcean Droplet
- **Service:** Ubuntu 22.04 Droplet ($6/month)
- **Location:** NYC3 (closest to target users)
- **Specs:** 1GB RAM, 1 vCPU, 25GB SSD
- **Stack:**
  - Python 3.13 (in venv)
  - Flask + Gunicorn
  - Nginx reverse proxy
  - SSL via Let's Encrypt
  - Supervisor for process management

### Frontend: Vercel (Free Tier)
- **Service:** Vercel Pro (free via GitHub Student Pack)
- **Build:** Next.js 15 static/SSR
- **CDN:** Global edge network
- **SSL:** Automatic HTTPS
- **Domain:** guardr.app → Vercel

### Environment Variables (DigitalOcean)
- OPEN_ROUTER_API_KEY
- OPENAI_API_KEY
- ANTHROPIC_API_KEY
- SERPER_API_KEY
- SCRAPINGBEE_API_KEY
- All other API keys from api-keys.zsh

---

## Deployment Steps

### Phase 1: Prepare DigitalOcean Droplet

1. **Create Droplet**
   ```bash
   # Via DigitalOcean web console
   - Ubuntu 22.04 LTS
   - Basic Plan: $6/month (1GB/1CPU)
   - Datacenter: NYC3
   - Add SSH key
   - Enable monitoring
   ```

2. **Initial Server Setup**
   ```bash
   ssh root@YOUR_DROPLET_IP

   # Create non-root user
   adduser guardr
   usermod -aG sudo guardr

   # Setup firewall
   ufw allow OpenSSH
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw enable

   # Update system
   apt update && apt upgrade -y
   ```

3. **Install Dependencies**
   ```bash
   # Python and tools
   apt install -y python3.13 python3.13-venv python3-pip nginx supervisor certbot python3-certbot-nginx

   # Install git
   apt install -y git
   ```

### Phase 2: Deploy Backend

4. **Clone Repository**
   ```bash
   su - guardr
   git clone https://github.com/calebmills99/Kallisto-OSINTer.git
   cd Kallisto-OSINTer
   ```

5. **Setup Python Environment**
   ```bash
   python3.13 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

6. **Configure Environment Variables**
   ```bash
   # Create .env file
   nano .env

   # Paste all API keys from api-keys.zsh
   # Format: KEY=value (one per line)
   ```

7. **Setup Gunicorn**
   ```bash
   # Create /home/guardr/Kallisto-OSINTer/gunicorn_config.py
   workers = 2
   bind = "127.0.0.1:8000"
   timeout = 300
   accesslog = "/var/log/guardr/access.log"
   errorlog = "/var/log/guardr/error.log"
   ```

8. **Setup Supervisor**
   ```bash
   # Create /etc/supervisor/conf.d/guardr.conf
   [program:guardr]
   directory=/home/guardr/Kallisto-OSINTer
   command=/home/guardr/Kallisto-OSINTer/venv/bin/gunicorn -c gunicorn_config.py guardr_api:app
   user=guardr
   autostart=true
   autorestart=true
   redirect_stderr=true
   stdout_logfile=/var/log/guardr/supervisor.log
   environment=PATH="/home/guardr/Kallisto-OSINTer/venv/bin"

   # Create log directory
   mkdir -p /var/log/guardr
   chown guardr:guardr /var/log/guardr

   # Start supervisor
   supervisorctl reread
   supervisorctl update
   supervisorctl start guardr
   ```

9. **Configure Nginx**
   ```nginx
   # /etc/nginx/sites-available/guardr-api
   server {
       listen 80;
       server_name api.guardr.app;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_read_timeout 300s;
           proxy_connect_timeout 300s;
       }
   }

   # Enable site
   ln -s /etc/nginx/sites-available/guardr-api /etc/nginx/sites-enabled/
   nginx -t
   systemctl reload nginx
   ```

10. **Setup SSL**
    ```bash
    certbot --nginx -d api.guardr.app
    ```

### Phase 3: Deploy Frontend (Vercel)

11. **Prepare Frontend Repository**
    ```bash
    cd /home/nobby/guardrV6-clean/website

    # Update .env.production
    echo "NEXT_PUBLIC_API_URL=https://api.guardr.app" > .env.production

    # Commit changes
    git add .
    git commit -m "Production config for Vercel"
    git push
    ```

12. **Deploy to Vercel**
    ```bash
    # Via Vercel Dashboard
    1. Import guardrV6 repository
    2. Framework: Next.js
    3. Root Directory: website/
    4. Environment Variables:
       - NEXT_PUBLIC_API_URL = https://api.guardr.app
    5. Deploy
    ```

### Phase 4: Configure DNS

13. **DNS Configuration**
    ```
    # At your domain registrar (Namecheap/Google Domains/etc)

    # For frontend (Vercel)
    Type: CNAME
    Name: @
    Value: cname.vercel-dns.com

    Type: CNAME
    Name: www
    Value: cname.vercel-dns.com

    # For backend API (DigitalOcean)
    Type: A
    Name: api
    Value: YOUR_DROPLET_IP
    ```

14. **Add Domain to Vercel**
    ```
    Vercel Dashboard → Project Settings → Domains
    - Add: guardr.app
    - Add: www.guardr.app
    ```

### Phase 5: Testing & Verification

15. **Health Checks**
    ```bash
    # Test backend API
    curl https://api.guardr.app/api/health

    # Test frontend
    curl https://guardr.app

    # Test full flow
    # Visit https://guardr.app and submit demo form
    ```

16. **Monitoring Setup**
    ```bash
    # Setup DigitalOcean monitoring alerts
    - CPU > 80%
    - Memory > 90%
    - Disk > 85%
    - Droplet offline

    # Setup uptime monitoring (UptimeRobot - free)
    - https://api.guardr.app/api/health
    - https://guardr.app
    ```

---

## Cost Breakdown

| Service | Cost | Notes |
|---------|------|-------|
| DigitalOcean Droplet | $6/month | Covered by $200 student credit |
| Vercel Pro | $0 | Free via GitHub Student Pack |
| Domain (guardr.app) | Already owned | - |
| SSL Certificates | $0 | Let's Encrypt |
| **Total** | **$6/month** | **~33 months free with credit** |

---

## Rollback Plan

If deployment fails:
1. Keep local server running
2. Debug production issues without downtime
3. DNS TTL is 1 hour - can revert quickly
4. Vercel has instant rollback to previous deployment

---

## Security Checklist

- [ ] SSH key-only authentication (disable password)
- [ ] Firewall configured (ufw)
- [ ] Non-root user for application
- [ ] SSL/HTTPS enforced
- [ ] API keys in environment variables (not in code)
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Regular security updates scheduled

---

## Maintenance Tasks

### Daily
- Monitor error logs: `tail -f /var/log/guardr/error.log`
- Check supervisor status: `supervisorctl status`

### Weekly
- Review API usage and costs
- Check disk space: `df -h`
- Review access logs for suspicious activity

### Monthly
- Update system packages: `apt update && apt upgrade`
- Renew SSL certificate (auto-renewed by certbot)
- Review and optimize database/cache if needed

---

## Next Steps

1. ✅ Create DigitalOcean account (if not already)
2. ✅ Verify GitHub Student Pack is active
3. ⬜ Create droplet and SSH in
4. ⬜ Follow Phase 1-5 deployment steps
5. ⬜ Test production thoroughly
6. ⬜ Shut down local servers
7. ⬜ Celebrate! 🎉
