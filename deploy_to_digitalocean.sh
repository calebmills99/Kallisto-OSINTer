#!/bin/bash
# DigitalOcean deployment automation script
# Run this ON THE DROPLET after initial SSH setup

set -e

echo "🚀 Guardr DigitalOcean Deployment Script"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as guardr user
if [ "$USER" != "guardr" ]; then
    echo -e "${RED}Error: This script must be run as 'guardr' user${NC}"
    echo "Run: sudo su - guardr"
    exit 1
fi

echo -e "${GREEN}✓${NC} Running as guardr user"
echo ""

# Update system
echo "📦 Installing system dependencies..."
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3-pip nginx supervisor certbot python3-certbot-nginx git

# Clone repository
echo ""
echo "📥 Cloning Kallisto-OSINTer repository..."
cd ~
if [ -d "Kallisto-OSINTer" ]; then
    echo -e "${YELLOW}Repository already exists, pulling latest...${NC}"
    cd Kallisto-OSINTer
    git pull
else
    git clone https://github.com/calebmills99/Kallisto-OSINTer.git
    cd Kallisto-OSINTer
fi

# Setup Python environment
echo ""
echo "🐍 Setting up Python virtual environment..."
python3.13 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Environment variables
echo ""
echo "🔐 Setting up environment variables..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file - YOU NEED TO EDIT THIS WITH YOUR API KEYS${NC}"
    cat > .env << 'EOF'
# Edit this file with your actual API keys
OPEN_ROUTER_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
SERPER_API_KEY=your_key_here
SCRAPINGBEE_API_KEY=your_key_here
EOF
    echo -e "${RED}⚠️  IMPORTANT: Edit ~/.Kallisto-OSINTer/.env with your API keys!${NC}"
    echo "Press Enter to continue..."
    read
fi

# Create log directory
echo ""
echo "📝 Creating log directory..."
sudo mkdir -p /var/log/guardr
sudo chown guardr:guardr /var/log/guardr

# Setup Gunicorn config
echo ""
echo "⚙️  Creating Gunicorn configuration..."
cat > gunicorn_config.py << 'EOF'
workers = 2
bind = "127.0.0.1:8000"
timeout = 300
accesslog = "/var/log/guardr/access.log"
errorlog = "/var/log/guardr/error.log"
loglevel = "info"
EOF

# Setup Supervisor
echo ""
echo "👁️  Configuring Supervisor..."
sudo tee /etc/supervisor/conf.d/guardr.conf > /dev/null << EOF
[program:guardr]
directory=/home/guardr/Kallisto-OSINTer
command=/home/guardr/Kallisto-OSINTer/venv/bin/gunicorn -c gunicorn_config.py guardr_api:app
user=guardr
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/guardr/supervisor.log
environment=PATH="/home/guardr/Kallisto-OSINTer/venv/bin"
EOF

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start guardr

# Configure Nginx
echo ""
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/guardr-api > /dev/null << 'EOF'
server {
    listen 80;
    server_name api.guardr.app;

    client_max_body_size 10M;

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
EOF

sudo ln -sf /etc/nginx/sites-available/guardr-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

echo ""
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Configure DNS: Point api.guardr.app to this droplet's IP"
echo "2. Wait for DNS propagation (~5-60 minutes)"
echo "3. Setup SSL: sudo certbot --nginx -d api.guardr.app"
echo "4. Test API: curl https://api.guardr.app/api/health"
echo ""
echo "Monitor logs:"
echo "  - Supervisor: tail -f /var/log/guardr/supervisor.log"
echo "  - Gunicorn: tail -f /var/log/guardr/error.log"
echo "  - Nginx: sudo tail -f /var/log/nginx/error.log"
echo ""
echo "Control service:"
echo "  - Status: sudo supervisorctl status guardr"
echo "  - Restart: sudo supervisorctl restart guardr"
echo "  - Stop: sudo supervisorctl stop guardr"
