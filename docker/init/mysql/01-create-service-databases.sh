#!/bin/sh
set -eu

mysql -uroot -p"$MYSQL_ROOT_PASSWORD" <<-EOSQL
CREATE DATABASE IF NOT EXISTS user_service CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS staff_service CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS payment_service CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS shipping_service CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON user_service.* TO '$MYSQL_USER'@'%';
GRANT ALL PRIVILEGES ON staff_service.* TO '$MYSQL_USER'@'%';
GRANT ALL PRIVILEGES ON payment_service.* TO '$MYSQL_USER'@'%';
GRANT ALL PRIVILEGES ON shipping_service.* TO '$MYSQL_USER'@'%';
FLUSH PRIVILEGES;
EOSQL
