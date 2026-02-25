#!/bin/bash
# SOCForge — TLS Certificate Automation (Let's Encrypt + Certbot)
# Usage: sudo ./scripts/setup_tls.sh socforge.example.com
# Requires: certbot, nginx installed

set -euo pipefail

DOMAIN="${1:?Usage: ./setup_tls.sh <domain>}"
EMAIL="${CERTBOT_EMAIL:-admin@${DOMAIN}}"
NGINX_CONF="/etc/nginx/sites-available/socforge.conf"

echo "=== SOCForge TLS Setup ==="
echo "Domain: ${DOMAIN}"
echo "Email:  ${EMAIL}"

# 1. Install certbot if missing
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    apt-get update && apt-get install -y certbot python3-certbot-nginx
fi

# 2. Obtain certificate
echo "Obtaining Let's Encrypt certificate..."
certbot certonly \
    --nginx \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    --domain "$DOMAIN" \
    --redirect

# 3. Update nginx config with actual domain
if [ -f "$NGINX_CONF" ]; then
    sed -i "s/socforge.example.com/${DOMAIN}/g" "$NGINX_CONF"
    echo "Updated nginx config with domain: ${DOMAIN}"
fi

# 4. Test nginx config
nginx -t

# 5. Reload nginx
systemctl reload nginx
echo "Nginx reloaded with TLS"

# 6. Setup auto-renewal cron
CRON_CMD="0 3 * * * certbot renew --quiet --deploy-hook 'systemctl reload nginx'"
(crontab -l 2>/dev/null | grep -v certbot; echo "$CRON_CMD") | crontab -
echo "Auto-renewal cron installed (daily 3 AM)"

# 7. Verify
echo ""
echo "=== Verification ==="
certbot certificates --domain "$DOMAIN"
echo ""
echo "Test: curl -I https://${DOMAIN}/api/health"
echo "=== TLS Setup Complete ==="
