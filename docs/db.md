# Database Documentation

## Overview
The database component of the Distributed POS system uses MySQL 8.0 to store events and plugin configurations. It's designed to be scalable, reliable, and easily accessible for event processing and analytics.

## Database Configuration
The database is configured using Docker with the following settings:

- **Image**: MySQL 8.0
- **Container Name**: pos_mysql
- **Database Name**: pos_db
- **Port**: 3306 (mapped to host)
- **Authentication**: Native password authentication

### Credentials
- **Root Password**: root
- **Database User**: pos_user
- **Database Password**: password

## Schema

### Events Table
Stores all POS events with their associated metadata:

```sql
CREATE TABLE IF NOT EXISTS events (
    event_id VARCHAR(255) PRIMARY KEY,
    type VARCHAR(255),
    store_id VARCHAR(255),
    data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### Fields
- `event_id`: Unique identifier for the event
- `type`: Type of the event (e.g., employee_login, basket_started)
- `store_id`: Identifier for the store where the event occurred
- `data`: JSON field containing event-specific data
- `created_at`: Timestamp of event creation

### Plugins Table
Manages plugin configurations and their states:

```sql
CREATE TABLE IF NOT EXISTS plugins (
    id VARCHAR(255) PRIMARY KEY,
    active BOOLEAN NOT NULL,
    filters JSON,
    actions JSON
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

#### Fields
- `id`: Unique identifier for the plugin
- `active`: Boolean indicating if the plugin is enabled
- `filters`: JSON configuration for event filtering
- `actions`: JSON configuration for plugin actions

## Setup and Installation

### Using Docker Compose
The database is automatically set up when running the Docker Compose configuration:

```bash
docker compose up -d
```

This will:
1. Create the MySQL container
2. Initialize the database with the schema
3. Set up the required user and permissions
4. Mount the initialization scripts

### Manual Setup
If setting up manually:

1. Create the database:
```sql
CREATE DATABASE pos_db;
```

2. Create the user:
```sql
CREATE USER 'pos_user'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON pos_db.* TO 'pos_user'@'%';
FLUSH PRIVILEGES;
```

3. Run the initialization script:
```bash
mysql -u pos_user -p pos_db < init.sql
```

## Data Persistence
- Database data is persisted using a Docker volume named `mysql_data`
- The volume is automatically created and managed by Docker Compose
- Data persists across container restarts

## Connection Details
- **Host**: localhost (when accessing from host machine)
- **Port**: 3306
- **Database**: pos_db
- **User**: pos_user
- **Password**: password

## Example Queries

### Query Events
```sql
-- Get all events
SELECT * FROM events;

-- Get events by type
SELECT * FROM events WHERE type = 'employee_login';

-- Get events within a time range
SELECT * FROM events 
WHERE created_at BETWEEN '2024-01-01' AND '2024-01-02';
```

### Query Plugins
```sql
-- Get active plugins
SELECT * FROM plugins WHERE active = true;

-- Get plugin configuration
SELECT id, filters, actions FROM plugins WHERE id = 'plugin_id';
```

## Maintenance

### Backup
To backup the database:
```bash
docker compose exec db mysqldump -u pos_user -ppassword pos_db > backup.sql
```

### Restore
To restore from backup:
```bash
docker compose exec -T db mysql -u pos_user -ppassword pos_db < backup.sql
```

### Monitoring
- Check container status: `docker compose ps db`
- View logs: `docker compose logs db`
- Connect to MySQL CLI: `docker compose exec db mysql -u pos_user -ppassword pos_db`

## Security Considerations
- The database is configured for development purposes
- For production:
  - Change default passwords
  - Restrict network access
  - Enable SSL/TLS
  - Implement proper backup strategies
  - Consider using secrets management
