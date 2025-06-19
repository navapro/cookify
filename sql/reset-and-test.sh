#!/bin/bash

# Database credentials
DB_USER="root"
DB_PASSWORD="judy123"
DB_NAME="cookify"

# 1. Reset the database
mysql -u"$DB_USER" -p"$DB_PASSWORD" -e "DROP DATABASE IF EXISTS $DB_NAME; CREATE DATABASE $DB_NAME;"

# 2. Create the tables
mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "cookify/sql/create_tables.sql"

# 3. Run the test queries
mysql -u"$DB_USER" -p"$DB_PASSWORD" -D "$DB_NAME" -t < "cookify/sql/test-sample.sql" 