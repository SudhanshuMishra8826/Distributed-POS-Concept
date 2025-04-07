# Distributed POS System

A modern, event-driven Point of Sale system built with microservices architecture, designed for scalability, flexibility, and real-time processing.

## System Architecture

The Distributed POS System is built on a modern event-driven architecture that decouples components and enables real-time processing of retail transactions. This architecture follows the principles of event sourcing and CQRS (Command Query Responsibility Segregation), allowing for high scalability and resilience.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Infrastructure Layer                           │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────┬───┤
│    Kafka    │    Redis    │    MySQL    │   Docker    │   Nginx     │   │
│  (Events)   │  (Caching)  │  (Storage)  │ (Container) │ (Reverse)   │   │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┴───┘
                           ▲
                           │
┌─────────────────────────────────────────────────────────────────────────┐
│                           Application Layer                              │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────┬───┤
│  Event      │  Plugin     │  Plugin     │  Event      │  Event      │   │
│ Generator   │ Management  │ Manager UI  │ Consumer    │ Consumer    │   │
│             │ Service     │ (Frontend)  │ Plugins     │ Plugins     │   │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┴───┘
                           ▲
                           │
┌─────────────────────────────────────────────────────────────────────────┐
│                           Plugin Layer                                  │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────────┬───┤
│   Age       │   Fraud     │  Customer   │ Purchase    │  Employee   │   │
│ Verification│ Detection   │   Lookup    │ Recommender │  Tracker    │   │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────────┴───┘
```

## Demo Video

Watch our comprehensive demo video to see the Distributed POS System in action:

[![Distributed POS System Demo](https://img.youtube.com/vi/placeholder/maxresdefault.jpg)](https://drive.google.com/file/d/17MPV1Q0F-1GJyz3o0YE_TLWRdAoxSKrP/view?usp=sharing)

The video demonstrates:
- Setting up the infrastructure services
- Starting the backend and frontend components
- Running the event generator
- Activating and testing each plugin
- Demonstrating the status check mechanism
- Showing the caching strategy in action

### Core Components

#### 1. Event Generator
- Simulates POS transactions by generating realistic retail events
- Produces events to Kafka topics for consumption by plugins
- Generates a complete transaction flow: employee login → basket creation → customer identification → item addition → subtotal calculation → payment → employee logout

#### 2. Plugin Management Service (Backend)
- FastAPI-based service for managing plugin lifecycle
- Provides RESTful API for plugin registration, activation/deactivation, and configuration
- Implements caching with Redis for efficient status checks
- Stores plugin metadata in MySQL for persistence

#### 3. Plugin Manager UI (Frontend)
- Next.js application with Tailwind CSS for a modern, responsive interface
- Provides intuitive management of plugins (create, read, update, delete)
- Real-time status updates and configuration management
- Responsive design for desktop and mobile access

#### 4. Event Consumer Plugins
- Independent microservices that process specific types of events
- Implement status checking to prevent unnecessary processing
- Available plugins:
  - **Age Verification**: Ensures compliance with age restrictions for alcohol purchases
  - **Fraud Detection**: Identifies potentially fraudulent transactions
  - **Customer Lookup**: Retrieves and caches customer information
  - **Purchase Recommender**: Suggests complementary products based on basket contents
  - **Employee Tracker**: Monitors employee login/logout and activity

#### 5. Infrastructure
- **Kafka**: Event streaming platform for reliable message delivery
- **Redis**: In-memory data store for caching and session management
- **MySQL**: Persistent storage for plugin metadata and transaction records
- **Docker**: Containerization for consistent deployment across environments

## Data Flow Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Event     │     │    Kafka    │     │   Plugin    │
│ Generator   │────▶│  (Events)   │────▶│ Management  │
└─────────────┘     └─────────────┘     │   Service   │
                                        └─────────────┘
                                              │
                                              ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Customer   │     │    Redis    │     │   Plugin    │
│   Lookup    │◀────│  (Caching)  │◀────│ Manager UI  │
└─────────────┘     └─────────────┘     └─────────────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│   Fraud     │     │    MySQL    │
│ Detection   │◀────│  (Storage)  │
└─────────────┘     └─────────────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Age       │     │ Purchase    │     │  Employee   │
│ Verification│     │ Recommender │     │  Tracker    │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Philosophical Approach

The architecture of this system is guided by several key principles:

### 1. Event-Driven Design
Events are the fundamental building blocks of the system. By modeling the system around events rather than state, we achieve:
- **Decoupling**: Components can evolve independently
- **Auditability**: Complete transaction history is preserved
- **Scalability**: Event processing can be distributed across multiple instances

### 2. Plugin-Based Architecture
The plugin system embodies the Open/Closed Principle - open for extension but closed for modification. This approach:
- **Enables Innovation**: New functionality can be added without changing existing code
- **Supports Specialization**: Each plugin can focus on a specific business concern
- **Facilitates Testing**: Plugins can be tested in isolation

### 3. Status-Aware Processing
The status check mechanism implemented across all plugins demonstrates a sophisticated approach to resource management:
- **Efficiency**: Inactive plugins don't consume resources
- **Graceful Degradation**: System continues to function even if some plugins are disabled
- **Operational Control**: Administrators can enable/disable functionality without deployment

### 4. Caching Strategy
The multi-level caching approach (Redis for plugin status, database for persistence) reflects a thoughtful balance between:
- **Performance**: Fast access to frequently used data
- **Consistency**: Reliable fallback mechanisms when cache misses occur
- **Resource Utilization**: Optimized use of memory and network resources

## System Requirements

### Development Environment
- Docker and Docker Compose
- Node.js 18.x or later (for frontend development)
- Python 3.9+ (for backend and plugins)
- Git for version control

### Production Environment
- **Hardware**:
  - CPU: 4+ cores
  - RAM: 8GB+ (16GB+ recommended)
  - Storage: 50GB+ SSD
- **Software**:
  - Linux-based OS (Ubuntu 20.04+ recommended)
  - Docker Engine 20.10+
  - Docker Compose 2.0+
  - Nginx or similar reverse proxy
  - SSL certificates for secure communication

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 18.x or later (for frontend development)
- Python 3.9+ (for backend and plugins)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Distributed-POS-Concept.git
cd Distributed-POS-Concept
```

2. Start the infrastructure services:
```bash
docker-compose up -d
```

3. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python plugin_service.py
```

4. Set up the frontend:
```bash
cd frontend
npm install
npm run dev
```

5. Run the event generator:
```bash
cd event-generator
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

6. Run any of the event consumer plugins:
```bash
cd event-consumers/[plugin-name]
# For Python plugins:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python plugin.py

# For JavaScript plugins:
npm install
npm start
```

### Accessing the System

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Kafka UI**: http://localhost:9001
- **MySQL**: localhost:3306
- **Redis**: localhost:6379

## API Documentation

The Plugin Management Service provides the following RESTful API endpoints:

### Plugin Management
- `GET /plugins/` - List all registered plugins
- `GET /plugins/{plugin_id}` - Get details of a specific plugin
- `POST /plugins/` - Register a new plugin
- `PUT /plugins/{plugin_id}` - Update a plugin's configuration
- `DELETE /plugins/{plugin_id}` - Delete a plugin

### Service Status
- `GET /services/status/{service_id}` - Get the current status of a service

## Monitoring and Logging

The system implements comprehensive logging across all components:

### Plugin Logging
- Each plugin implements a standardized logging system
- Logs are written to both console and file
- Log levels (INFO, DEBUG, WARNING, ERROR) provide appropriate detail
- Log files are stored in the plugin's directory (e.g., `employee-tracker.log`)

### Status Monitoring
- Plugin status is cached in Redis for efficient checking
- Inactive plugins log warnings when events are skipped
- The frontend UI provides real-time status updates

## Security Considerations

### Authentication and Authorization
- The frontend and backend communicate securely
- API endpoints should be protected in production environments
- Consider implementing JWT authentication for API access

### Data Protection
- Sensitive data is stored securely in the database
- Redis caching implements appropriate expiration times
- Consider encrypting data at rest in production environments

### Network Security
- Use HTTPS for all external communications
- Implement appropriate firewall rules
- Consider using a reverse proxy for additional security

## Troubleshooting Guide

### Common Issues

1. **Kafka Connection Issues**
   - Ensure Kafka is running: `docker-compose ps`
   - Check Kafka logs: `docker-compose logs kafka`
   - Verify topic creation: Access Kafdrop UI at http://localhost:9001

2. **Plugin Status Check Failures**
   - Verify Redis connection: `docker-compose logs redis`
   - Check plugin registration in the database
   - Ensure the backend service is running

3. **Frontend Connection Issues**
   - Verify the backend API is running
   - Check CORS configuration in the backend
   - Clear browser cache and reload

4. **Database Connection Issues**
   - Ensure MySQL is running: `docker-compose ps`
   - Check MySQL logs: `docker-compose logs db`
   - Verify database credentials in environment files

## Development Workflow

1. **Plugin Development**:
   - Create a new plugin in the `event-consumers` directory
   - Implement the status check mechanism using the utility functions
   - Register the plugin with the backend service

2. **Testing**:
   - Use the event generator to produce test events
   - Verify plugin behavior with different event types
   - Test plugin activation/deactivation through the UI

3. **Deployment**:
   - Package plugins as Docker containers
   - Update the docker-compose.yaml file
   - Deploy to your target environment

## Project Structure

```
Distributed-POS-Concept/
├── backend/                      # FastAPI plugin management service
│   ├── plugin_service.py         # Main FastAPI application with plugin management endpoints
│   └── requirements.txt          # Python dependencies for the backend service
│
├── database/                     # Database initialization scripts
│   └── init.sql                  # SQL script to create necessary database tables
│
├── docs/                         # Documentation files
│
├── docker-compose.yaml           # Docker services configuration for infrastructure components
│
├── event-consumers/              # Event processing plugins
│   ├── age-verification/         # Age verification plugin
│   │   ├── plugin.py             # Main plugin implementation for age verification
│   │   └── requirements.txt      # Python dependencies for the plugin
│   │
│   ├── customer-lookup/          # Customer lookup plugin
│   │   ├── plugin.py             # Main plugin implementation for customer lookup
│   │   └── requirements.txt      # Python dependencies for the plugin
│   │
│   ├── employee-tracker/         # Employee tracking plugin
│   │   ├── plugin.py             # Main plugin implementation for employee tracking
│   │   ├── requirements.txt      # Python dependencies for the plugin
│   │   └── employee-tracker.log  # Log file for the plugin
│   │
│   ├── fraud-detection/          # Fraud detection plugin
│   │   ├── plugin.js             # Main plugin implementation for fraud detection
│   │   ├── package.json          # Node.js dependencies for the plugin
│   │   └── package-lock.json     # Locked versions of Node.js dependencies
│   │
│   ├── purchase-recommender/      # Purchase recommendation plugin
│   │   ├── plugin.js             # Main plugin implementation for purchase recommendations
│   │   ├── package.json          # Node.js dependencies for the plugin
│   │   └── package-lock.json     # Locked versions of Node.js dependencies
│   │
│   ├── utils.py                  # Python utility functions for status checking and logging
│   ├── utils.js                  # JavaScript utility functions for status checking and logging
│   ├── package.json              # Node.js dependencies for JavaScript plugins
│   └── package-lock.json         # Locked versions of Node.js dependencies
│
├── event-generator/              # Event generation service
│   ├── generator.py              # Main event generation logic
│   ├── main.py                   # Entry point for the event generator
│   ├── models.py                 # Data models for generated events
│   └── requirements.txt          # Python dependencies for the event generator
│
├── frontend/                     # Next.js frontend application
│   ├── src/                      # Source code for the frontend
│   │   ├── app/                  # Next.js app directory
│   │   │   ├── page.tsx          # Main page component
│   │   │   ├── create/           # Create plugin page
│   │   │   │   └── page.tsx      # Create plugin component
│   │   │   ├── edit/             # Edit plugin page
│   │   │   │   └── [id]/         # Dynamic route for plugin ID
│   │   │   │       └── page.tsx  # Edit plugin component
│   │   │   └── layout.tsx        # Root layout component
│   │   │
│   │   ├── components/           # Reusable UI components
│   │   │   ├── Header.tsx        # Header component
│   │   │   ├── PluginCard.tsx    # Plugin card component
│   │   │   ├── PluginForm.tsx    # Plugin form component
│   │   │   └── LoadingSpinner.tsx# Loading spinner component
│   │   │
│   │   └── utils/                # Utility functions
│   │       └── api.ts            # API client functions
│   │
│   ├── public/                   # Static assets
│   ├── package.json              # Node.js dependencies for the frontend
│   ├── package-lock.json         # Locked versions of Node.js dependencies
│   ├── next.config.js            # Next.js configuration
│   ├── tailwind.config.js        # Tailwind CSS configuration
│   ├── postcss.config.js         # PostCSS configuration
│   └── tsconfig.json             # TypeScript configuration
│
└── README.md                     # This documentation file
```


