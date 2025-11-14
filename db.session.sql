$env:MYSQL_USER = 'root'
$env:MYSQL_PASSWORD = '1234'   # replace with actual password (e.g. 1234)
$env:MYSQL_HOST = '127.0.0.1'        # prefer 127.0.0.1 over localhost to force TCP
$env:MYSQL_PORT = '3306'
$env:MYSQL_DATABASE = 'hrms_db'

# Optionally (app also supports DATABASE_URL)
$env:DATABASE_URL = "mysql+pymysql://$($env:MYSQL_USER):$($env:MYSQL_PASSWORD)@$($env:MYSQL_HOST):$($env:MYSQL_PORT)/$($env:MYSQL_DATABASE)"
# Ensure SKIP_DB_INIT is false so init runs
$env:SKIP_DB_INIT = '0'