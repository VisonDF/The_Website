
```

python3 -m venv menv

source menv/bin/activate

pip install -r requirements.txt

node -v

npm -v

npm init -y

npm install --save-dev esbuild

npm install \
  @codemirror/state \
  @codemirror/view \
  @codemirror/commands \
  @codemirror/lang-html \
  @codemirror/language \
  @codemirror/autocomplete \
  @codemirror/theme-one-dark

npx esbuild static/js/editor.js \
  --bundle \
  --format=esm \
  --platform=browser \
  --minify \
  --outfile=static/js/editor.bundle.js

```


```

mysql -u root -p


-- Create database
CREATE DATABASE df_engine_site
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER 'df_user'@'localhost'
  IDENTIFIED BY 'user_password';

-- Grant privileges
GRANT ALL PRIVILEGES
  ON df_engine_site.*
  TO 'df_user'@'localhost';

-- Apply changes
FLUSH PRIVILEGES;

mysql -u df_user -p df_engine_site < database_structure.sql

// update config.py matching credentials

```

```

// update set_pass.py to give strong password for website admin
python3 set_pass.py

```

```
gunicorn -w 4 -b 0.0.0.0:8089 run:app

```

Or making it persistent

```

[Unit]
Description=VisonDF Website (Gunicorn)
After=network.target

[Service]
User=www-data
Group=www-data

WorkingDirectory=/var/www/visondf/The_Website

Environment="FLASK_ENV=production"
EnvironmentFile=/var/www/visondf/The_Website/.env

ExecStart=/var/www/visondf/The_Website/menv/bin/gunicorn \
    --workers 2 \
    --bind 127.0.0.1:8089 \
    run:app

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target


```

```
mkdir -p /var/www/visondf
mv /root/The_Website /var/www/visondf/
chown -R www-data:www-data /var/www/visondf
chown -R www-data:www-data /var/www/visondf/The_Website/builds
chmod -R u+rwX /var/www/visondf/The_Website/builds
```

good dfengine.conf

```

upstream backend {
    server 127.0.0.1:8089;
    keepalive 64;
}

server {

    listen 80;
    server_name visondf.dev www.visondf.dev;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name visondf.dev www.visondf.dev;

    ssl_certificate /etc/letsencrypt/live/visondf.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/visondf.dev/privkey.pem;

    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1h;
    ssl_session_tickets off;
    ssl_protocols TLSv1.2 TLSv1.3;

    # -------------------------
    # STATIC SITE (public pages)
    # -------------------------
    root /var/www/visondf/The_Website/builds;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    # -------------------------
    # STATIC ASSETS
    # -------------------------
    location /static/ {
        alias /var/www/visondf/The_Website/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # -------------------------
    # ADMIN (Flask / Gunicorn)
    # -------------------------
    location /admin/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;

        proxy_connect_timeout 2s;
        proxy_read_timeout 30s;
    }

    location /login {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;

        proxy_connect_timeout 2s;
        proxy_read_timeout 30s;
    }

    location /logout {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;

        proxy_connect_timeout 2s;
        proxy_read_timeout 30s;
    }


}

```

good nginx.conf:

```
user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 4096;
    multi_accept on;
}

http {

    ##
    # Basic Settings
    ##

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;

    keepalive_timeout 65;
    keepalive_requests 1000;

    types_hash_max_size 2048;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    ##
    # SSL Settings (modern & safe)
    ##

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1h;
    ssl_session_tickets off;

    ##
    # Logging Settings
    ##

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log warn;

    ##
    # Compression (Gzip)
    ##

    gzip on;
    gzip_comp_level 5;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_vary on;

    gzip_types
        text/plain
        text/css
        text/javascript
        application/javascript
        application/json
        application/xml
        application/xml+rss
        application/xhtml+xml
        image/svg+xml;

    ##
    # Compression (Brotli — optional but recommended)
    ##

    # Uncomment if brotli module is available
    # brotli on;
    # brotli_comp_level 5;
    # brotli_types
    #     text/plain
    #     text/css
    #     text/javascript
    #     application/javascript
    #     application/json
    #     application/xml
    #     image/svg+xml;

    ##
    # Virtual Host Configs
    ##

    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}

```





