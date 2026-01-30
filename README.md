
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
gunicorn -w 2 -b 127.0.0.1:8089 run:app

```





