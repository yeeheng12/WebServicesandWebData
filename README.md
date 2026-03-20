# House Sales and Energy Efficiency API

## 1. Project Overview

The House Sales and Energy Efficiency API is a RESTful web service designed to provide structured access to UK residential property sales data enriched with Energy Performance Certificate (EPC) and location information. The system integrates multiple datasets into a unified backend service, enabling both record-level data retrieval and higher-level analytical exploration.

The API is built using FastAPI with a relational database backend and exposes well-defined HTTP endpoints for interacting with property, energy, and location data. It also includes analytical capabilities such as price trends, EPC distributions, and location-based comparisons, allowing users to explore relationships between housing prices and energy efficiency.

Developed for the COMP3011 Web Services and Web Data module, the project demonstrates key software engineering principles including RESTful design, database integration, authentication, testing, and deployment readiness. The system is designed as a complete backend service with clear structure, maintainability, and extensibility.

---

## 2. Objectives and Scope

The primary objective of this project is to design and implement a robust, data-driven RESTful API that supports secure access, management, and analysis of UK housing data.

The system aims to:
- Provide structured access to property and EPC data through RESTful endpoints  
- Support full CRUD operations for core resources  
- Enable flexible querying using filtering, sorting, and pagination  
- Deliver analytical insights such as price trends and EPC distributions  
- Enforce secure access control using JWT-based authentication and role-based authorization  

The scope of the project is limited to backend API development. The system operates on a preprocessed dataset and focuses on descriptive analytics rather than predictive modelling. While the API is designed to be deployment-ready, advanced production features such as distributed scaling and monitoring are not fully implemented within this coursework.

---

## 3. Key Features

The API provides the following core features:

### RESTful Design
- Resource-based endpoints using standard HTTP methods (GET, POST, PUT, DELETE)  
- Consistent URI structure and JSON response format  

### CRUD Operations
- Create, retrieve, update, and delete property and energy certificate records  
- Support for partial updates and data integrity constraints  

### Advanced Querying
- Filtering by location, price range, date, property type, and energy rating  
- Sorting and pagination for efficient data retrieval  

### Analytical Capabilities
- Price trends over time  
- EPC rating distributions  
- Price vs energy efficiency comparisons  
- Area-based rankings and comparisons  

### Authentication and Authorization
- JWT-based authentication (OAuth2 password flow)  
- Role-based access control (viewer, editor, admin)  

### Data Validation and Error Handling
- Input validation using Pydantic schemas  
- Standardised error responses and status codes  

### Testing and Reliability
- Automated testing using pytest  
- Coverage of authentication, CRUD operations, analytics, and validation  

### Data Processing Pipeline
- Preprocessing scripts for cleaning and merging datasets  
- Deployment-ready dataset for efficient seeding  

### Documentation and Metadata
- Interactive API documentation (`/docs`, `/redoc`)  
- Service metadata (`/info`) and health check (`/health`) endpoints  

---

## 4. System Architecture

The API follows a layered architecture that separates concerns between request handling, business logic, and data persistence. This structure improves maintainability, testability, and scalability, and aligns with best practices for web service design.

### High-Level Architecture

The system can be viewed as a three-layer architecture:

1. **Presentation Layer (API Layer)**  
   - Implemented using FastAPI  
   - Handles HTTP requests and responses  
   - Defines routes for resources such as authentication, properties, energy certificates, locations, and analytics  
   - Performs input validation via Pydantic schemas  

2. **Application Layer (Business Logic)**  
   - Contains the core logic for processing requests  
   - Implements validation rules, filtering, aggregation, and analytics  
   - Coordinates interactions between the API layer and the database  
   - Ensures consistent behaviour across endpoints  

3. **Data Layer (Persistence Layer)**  
   - Managed using SQLAlchemy ORM  
   - Defines relational models (User, PropertyRecord, EnergyCertificate)  
   - Handles database queries, transactions, and relationships  
   - Supports both SQLite (development) and PostgreSQL (production)

### Component Interaction

A typical request follows this flow:
1. Client sends an HTTP request to an endpoint (e.g. `/properties`)  
2. FastAPI router receives the request and validates input using schemas  
3. The request is passed to the application logic (CRUD or analytics functions)  
4. SQLAlchemy interacts with the database to retrieve or modify data  
5. The result is formatted into a structured JSON response  
6. The response is returned to the client  

### Modular Design

The project is organised into modules to enforce separation of concerns:
- **routers/** → defines API endpoints and request handling  
- **models/** → defines database schema  
- **schemas/** → defines request/response validation  
- **crud/** → encapsulates database operations  
- **security/** → handles authentication and token management  
- **dependencies/** → shared utilities (e.g. database sessions, user context)  

This modular approach makes the system easier to extend, test, and maintain.

### Stateless Design

The API follows a stateless architecture:
- Each request contains all required information (including authentication tokens)  
- No server-side session state is stored  
- Improves scalability and aligns with REST principles  

### Data Flow and Processing

The system relies on a preprocessed dataset:
- Data is cleaned and merged using standalone scripts  
- The processed dataset is loaded into the database during seeding  
- The API operates only on structured, validated data  

This separation ensures that data preparation does not impact runtime performance.

### Scalability Considerations

Although designed for coursework, the architecture supports future scaling:
- Database abstraction allows switching from SQLite to PostgreSQL  
- Modular structure supports adding new endpoints or services  
- Stateless design enables horizontal scaling of the API  

Overall, the system architecture provides a clear, maintainable foundation for building a reliable, extensible RESTful API.

## 5. Technology Stack

The API is built using a modern Python-based technology stack chosen for performance, developer productivity, and suitability for RESTful service design. Each component plays a specific role in ensuring the system is robust, maintainable, and scalable.

### Backend Framework
- **FastAPI**
  - High-performance web framework for building APIs  
  - Provides automatic OpenAPI (Swagger) documentation  
  - Supports asynchronous request handling  
  - Built-in validation using Python type hints  

### Database
- **SQLite (Development)**
  - Lightweight, file-based database used for local development and testing  
  - Requires minimal configuration  

- **PostgreSQL (Production-ready)**
  - Supported via `DATABASE_URL` configuration  
  - Suitable for handling larger datasets and concurrent access  
  - Enables easier deployment to cloud environments  

### Object Relational Mapping (ORM)
- **SQLAlchemy**
  - Provides an abstraction layer for interacting with the database  
  - Supports relational modelling (tables, relationships, constraints)  
  - Enables flexible and complex query construction  

### Data Validation and Serialization
- **Pydantic**
  - Used for request and response validation  
  - Ensures type safety and data consistency  
  - Automatically integrates with FastAPI for input validation  

### Authentication and Security
- **JWT (JSON Web Tokens)**
  - Stateless authentication mechanism  
  - Tokens are issued upon login and included in request headers  
  - Enables secure access to protected endpoints  

- **OAuth2 Password Flow**
  - Used for handling login and token generation  
  - Integrated with FastAPI security utilities  

### Data Processing
- **Pandas**
  - Used in preprocessing scripts for:
    - Cleaning raw datasets  
    - Merging property, EPC, and location data  
    - Transforming data into API-ready format  

### Testing
- **Pytest**
  - Framework for automated testing  
  - Supports fixtures, parametrisation, and modular test design  
  - Used to test authentication, CRUD operations, analytics, and validation  

### Development and Deployment Tools
- **Uvicorn**
  - ASGI server used to run the FastAPI application  
  - Supports hot-reload during development  

- **Environment Variables**
  - Used for configuration (e.g. database URL, JWT secret)  
  - Enables separation between development and production settings  

### Summary

The chosen technology stack ensures:
- High performance and responsiveness (FastAPI + Uvicorn)  
- Strong data integrity and validation (SQLAlchemy + Pydantic)  
- Secure and scalable authentication (JWT + OAuth2)  
- Efficient data handling and preprocessing (Pandas)  
- Reliable and repeatable testing (Pytest)  

This combination provides a solid foundation for building a production-ready RESTful API while remaining accessible and maintainable within the scope of the coursework.

## 6. Dataset and Data Processing Pipeline

The API is built on a processed and enriched dataset that combines multiple real-world data sources into a single, consistent structure suitable for both transactional operations and analytical queries. The data pipeline is a key component of the system, as it ensures that the API operates on clean, reliable, and well-structured data.

### Data Sources

The dataset is derived from the following sources:

- **UK Property Price Paid Data**  
  - Contains residential property transaction records  
  - Includes attributes such as price, sale date, postcode, and property type  

- **Energy Performance Certificate (EPC) Data**  
  - Provides information on property energy efficiency  
  - Includes energy ratings, efficiency scores, and floor area  

- **Location and Postcode Data**  
  - Adds geographic context to properties  
  - Enables grouping and analysis by area (e.g. town/city, district, county)  

Individually, these datasets are incomplete for analytical purposes. The pipeline integrates them to create a unified view of each property.

---

### Data Processing Pipeline

The data preparation process is implemented through dedicated scripts and follows a structured pipeline:

1. **Data Cleaning**
   - Removal of invalid or inconsistent records  
   - Standardisation of formats (e.g. postcodes, categorical values)  
   - Handling of missing or null-like values  

2. **Dataset Preparation**
   - Separation of sales data and EPC/location data  
   - Reduction of unnecessary fields to optimise dataset size  
   - Validation of key attributes such as price, date, and energy ratings  

3. **Data Merging**
   - Joining datasets primarily on postcode and related identifiers  
   - Linking property records with corresponding EPC information  
   - Ensuring referential consistency between merged records  

4. **Feature Engineering and Transformation**
   - Renaming and restructuring fields for API compatibility  
   - Deriving additional attributes where required (e.g. combined address fields)  
   - Normalising numerical values such as efficiency scores  

5. **Output Generation**
   - Saving the final dataset as a structured CSV file  
   - Producing:
     - A full dataset for completeness  
     - A reduced deployment dataset for faster seeding  

---

### Dataset Characteristics

- Approximately **790,000+ property records** after processing  
- Over **50 attributes per record**, including transactional, energy, and location data  
- High coverage of EPC-linked properties, with a small proportion of unmatched records  
- Suitable for both:
  - CRUD operations (record-level access)  
  - Analytical queries (aggregation and comparison)

---

### Integration with the API

The processed dataset is not queried directly. Instead:

- It is **loaded into the database** using a seeding script  
- The API operates on structured relational tables derived from the dataset  
- This separation ensures:
  - Faster query performance  
  - Better data integrity through constraints  
  - Easier maintenance and extensibility  

---

### Design Considerations

- **Preprocessing outside the API runtime**  
  Reduces overhead during request handling and improves performance  

- **Use of a deployment dataset**  
  Allows faster setup and testing without processing the full dataset  

- **Data consistency and validation**  
  Ensures reliable analytical results and prevents invalid data from entering the system  

---

Overall, the data processing pipeline transforms raw, heterogeneous datasets into a clean, unified data model that underpins all API functionality, enabling efficient data access and meaningful analysis of the UK housing market.

## 7. Data Model and Database Design

The API is built on a relational database model designed to support both transactional operations (CRUD) and analytical queries efficiently. The schema reflects the structure of the processed dataset while ensuring data integrity, consistency, and extensibility.

The design separates core entities into distinct tables and uses relationships to link related data, allowing flexible querying and clear organisation of information.

---

### 7.1 Entities and Relationships

The system is centred around three primary entities:

- **User**
  - Stores authentication and authorization data  
  - Attributes include username, email, hashed password, role, and audit fields  
  - Used to control access to protected endpoints  

- **PropertyRecord**
  - Represents individual property sale transactions  
  - Includes attributes such as transaction ID, price, sale date, postcode, property type, and location fields  
  - Also stores energy-related attributes (e.g. current rating, efficiency) for quick access  
  - Contains audit fields linking to the user who created or updated the record  

- **EnergyCertificate**
  - Stores detailed EPC information for properties  
  - Includes attributes such as energy ratings, efficiency scores, and floor area  
  - Linked to PropertyRecord via a foreign key relationship  

#### Relationships

- **One-to-Many (Property → EnergyCertificate)**  
  A single property can have multiple energy certificates, reflecting updates or historical EPC records  

- **User Relationships**  
  Property and energy certificate records store references to the user who created or updated them, supporting traceability and auditability  

This relational structure ensures that:
- Data is normalised and avoids unnecessary duplication  
- Relationships can be efficiently queried  
- The system can be extended with additional entities if required  

---

### 7.2 Schema Design Decisions

Several design decisions were made to balance performance, usability, and data integrity:

- **Separation of Core Entities**  
  Properties and energy certificates are stored in separate tables to maintain a clear data model and avoid excessive duplication of EPC data  

- **Partial Denormalisation for Performance**  
  Key EPC attributes (e.g. current energy rating and efficiency) are also stored in the PropertyRecord table  
  - This allows faster filtering and analytics without requiring joins for every query  

- **Use of Unique Constraints**  
  - Transaction IDs are enforced as unique to prevent duplicate property records  
  - EPC identifiers (e.g. lmk_key) are also unique to ensure data consistency  

- **Audit Fields**  
  - Fields such as `created_by_user_id` and `updated_by_user_id` are included  
  - Enables tracking of changes and supports role-based operations  

- **Flexible Schema for Filtering**  
  - Fields such as postcode, town/city, and property type are explicitly stored  
  - Enables efficient filtering without requiring complex transformations  

- **Validation at Schema Level**  
  - Input validation is handled using Pydantic schemas  
  - Ensures only valid data enters the database (e.g. valid EPC ratings, positive prices)  

These decisions reflect a balance between strict normalisation and practical API performance.

---

### 7.3 Indexing and Performance Considerations

To ensure efficient query performance, especially given the dataset size (~790k records), several optimisations are considered:

- **Indexing Frequently Queried Fields**
  - Postcode  
  - Town/City  
  - Price  
  - Sale date  
  - Energy rating  

  These fields are commonly used in filtering, sorting, and analytics queries.

- **Optimised Query Design**
  - Filtering and pagination reduce the amount of data returned per request  
  - Sorting is limited to supported fields to prevent inefficient queries  

- **Use of Deployment Dataset**
  - A reduced dataset is used for development and testing  
  - Improves performance during seeding and local execution  

- **Separation of Analytical Logic**
  - Aggregations (e.g. averages, trends) are handled in dedicated endpoints  
  - Prevents overloading standard CRUD operations  

- **Database Flexibility**
  - SQLite is used for local development due to its simplicity  
  - PostgreSQL can be used in production for improved performance, indexing, and concurrency handling  

- **Stateless API Design**
  - No server-side session storage  
  - Allows scaling across multiple instances if deployed  

Overall, the database design supports both efficient transactional access and analytical queries while maintaining data integrity and scalability within the scope of the project.

## 8. API Design

The API is designed following RESTful principles to ensure consistency, scalability, and ease of use. It provides a clear resource-oriented structure, predictable request/response patterns, and standardised error handling.

---

### 8.1 RESTful Principles Applied

The API adheres to key REST architectural principles:

- **Resource-Based Design**  
  All endpoints are structured around core resources such as properties, energy certificates, users, locations, and analytics.

- **Statelessness**  
  Each request contains all necessary information (including authentication tokens).  
  No server-side session state is maintained.

- **Standard HTTP Methods**  
  - `GET` → retrieve data  
  - `POST` → create resources  
  - `PUT` → update resources  
  - `DELETE` → remove resources  

- **Uniform Interface**  
  Consistent endpoint structures and response formats are used across all resources.

- **Client-Server Separation**  
  The backend API is independent from any frontend implementation.

- **Hypermedia (HATEOAS)**  
  Certain endpoints (e.g. location summaries) include links to related resources to improve discoverability.

---

### 8.2 Resource Structure and URI Design

Resources are organised using clear and hierarchical URI patterns:

- **Authentication**
  - `/auth/register`
  - `/auth/login`
  - `/auth/me`

- **Properties**
  - `/properties`
  - `/properties/{id}`

- **Energy Certificates**
  - `/energy-certificates`
  - `/energy-certificates/{id}`

- **Locations**
  - `/locations/{postcode}/summary`

- **Analytics**
  - `/analytics/price-trend`
  - `/analytics/energy-price-impact`
  - `/analytics/top-areas`
  - `/analytics/epc-distribution`

#### Design Characteristics

- Plural resource naming (e.g. `/properties`)  
- Use of path parameters for specific resources  
- Logical grouping of endpoints by domain  
- Query parameters for filtering, sorting, and pagination  

This structure ensures the API is intuitive, predictable, and easy to navigate.

---

### 8.3 Request and Response Format

The API uses JSON as the standard format for all requests and responses.

#### Request Handling

- Requests are validated using Pydantic schemas  
- Ensures:
  - Correct data types  
  - Required fields are present  
  - Invalid data is rejected early  

Example request:
```json
{
  "price": 250000,
  "postcode": "LS1 1AA",
  "property_type": "F"
}
```
#### Response Structure

- Successful responses return:
  - Appropriate HTTP status codes (e.g. `200`, `201`)
  - Structured JSON objects

- List endpoints support pagination metadata:
  - `total`
  - `limit`
  - `offset`

Example response:
{
  "id": 1,
  "price": 250000,
  "postcode": "LS1 1AA"
}

---

### 8.4 Error Handling Strategy

The API implements a consistent and standardised error handling approach.

#### HTTP Status Codes

- `200 OK` → successful request
- `201 Created` → resource created
- `400 Bad Request` → invalid input
- `401 Unauthorized` → authentication required/failed
- `403 Forbidden` → insufficient permissions
- `404 Not Found` → resource does not exist
- `409 Conflict` → duplicate or conflicting data
- `422 Unprocessable Entity` → validation errors

#### Validation Errors

- Automatically handled by FastAPI and Pydantic
- Provide clear details about invalid fields

#### Custom Error Handling

- Explicit checks for:
  - Missing resources
  - Duplicate entries
  - Invalid query parameters

#### Security Errors

- Authentication failures return `401`
- Authorization failures return `403`

#### Consistency

- All errors return structured JSON responses
- Error messages are designed to be clear and informative

---

Overall, the API design provides a clean, consistent, and predictable interface that aligns with RESTful best practices while supporting both standard CRUD operations and advanced analytical queries.

## 9. Authentication and Authorization

The API implements secure, stateless authentication using JSON Web Tokens (JWT) combined with role-based access control (RBAC). This ensures that only authorised users can access protected resources while maintaining scalability and simplicity.

---

### 9.1 Authentication Flow

The authentication process follows a standard token-based workflow:

1. **User Registration**
   - Endpoint: `POST /auth/register`
   - Users provide username, email, password, and role
   - Passwords are securely hashed before storage

2. **User Login**
   - Endpoint: `POST /auth/login`
   - Users authenticate using username/email and password
   - If credentials are valid, a JWT access token is issued

3. **Token Usage**
   - The client includes the token in subsequent requests:
     ```
     Authorization: Bearer <access_token>
     ```
   - Required for all protected endpoints

4. **Accessing Protected Resources**
   - The API validates the token and retrieves the current user
   - Access is granted or denied based on authentication and role

This flow ensures that authentication is stateless and does not require server-side session storage.

---

### 9.2 JWT Implementation

JWT is used as the core authentication mechanism due to its simplicity and scalability.

#### Key Characteristics

- **Stateless Authentication**
  - No session data stored on the server
  - Each request is independently authenticated

- **Token Generation**
  - Tokens are generated upon successful login
  - Signed using a secret key (`JWT_SECRET_KEY`)

- **Token Contents**
  - Includes user identifier (e.g. user ID or username)
  - Includes token expiry time

- **Token Expiry**
  - Controlled via `ACCESS_TOKEN_EXPIRE_MINUTES`
  - Prevents long-lived tokens and reduces security risk

#### Token Validation

- Tokens are validated on each request:
  - Signature verification
  - Expiry check
  - User existence check

- Invalid or expired tokens result in:
  - `401 Unauthorized` responses

#### Security Considerations

- Passwords are hashed before storage (not stored in plaintext)
- Secret keys are managed via environment variables
- Tokens must be transmitted securely (e.g. HTTPS in production)

---

### 9.3 Role-Based Access Control

The API enforces role-based access control to restrict operations based on user permissions.

#### Defined Roles

- **viewer**
  - Read-only access
  - Can retrieve data but cannot modify it

- **editor**
  - Can create and update resources
  - Cannot perform delete operations

- **admin**
  - Full access to all operations
  - Can create, update, and delete resources

#### Enforcement Mechanism

- Role checks are implemented via dependency injection
- Each protected endpoint specifies required roles
- Requests are validated before executing business logic

#### Example Access Rules

- `GET /properties` → accessible to all roles  
- `POST /properties` → editor and admin only  
- `DELETE /properties/{id}` → admin only  

#### Error Handling

- Unauthenticated requests → `401 Unauthorized`  
- Insufficient permissions → `403 Forbidden`  

---

Overall, the authentication and authorization system ensures secure access control while maintaining a scalable and stateless API design aligned with RESTful principles.

## 10. Project Structure

The project follows a modular and layered structure to ensure separation of concerns, maintainability, and scalability. Each component is organised based on its responsibility within the system, making the codebase easier to navigate and extend.

### Directory Structure
```
project-root/
│
├── app/
│   ├── main.py                     # FastAPI application entry point
│   ├── models.py                   # SQLAlchemy ORM models
│   ├── schemas.py                  # Pydantic request/response schemas
│   ├── crud.py                     # Database access and business logic
│   ├── database.py                 # Database connection and session setup
│   ├── dependencies.py             # Shared dependencies (DB session, auth)
│   ├── security.py                 # JWT authentication and password hashing
│   │
│   └── routers/
│       ├── auth.py                 # Authentication endpoints
│       ├── properties.py           # Property CRUD endpoints
│       ├── energy_certificates.py  # EPC CRUD endpoints
│       ├── locations.py            # Location-based endpoints
│       └── analytics.py            # Analytical endpoints
│
├── scripts/
│   ├── build_property_dataset.py   # Dataset merging and preparation
│   ├── clean_all_data.py           # Data cleaning pipeline
│   ├── make_deploy_dataset.py      # Reduced dataset generation
│   └── seed_data.py                # Database seeding script
│
├── data/
│   ├── raw/                        # Original unprocessed datasets
│   │   ├── all-domestic-certificates/
│   │   ├── NSPL_FEB_2026_UK.csv    # Postcode/location dataset
│   │   └── pp-complete.csv         # Raw price paid dataset
│   │
│   └── processed/                  # Cleaned and merged datasets
│       ├── certificates_clean.csv
│       ├── certificates_with_location.csv
│       ├── nspl_clean.csv
│       ├── price_paid_clean.csv
│       ├── property_records.csv           # Full merged dataset
│       ├── property_records_deploy.csv    # Reduced deployment dataset
│       └── recommendations_clean.csv
│
├── tests/
│   ├── conftest.py               # Test configuration and fixtures
│   ├── test_auth.py              # Authentication tests
│   ├── test_properties.py        # Property endpoint tests
│   ├── test_energy_certificates.py # EPC tests
│   ├── test_locations.py         # Location tests
│   ├── test_analytics.py         # Analytics tests
│   ├── test_security.py          # Security and RBAC tests
│   ├── test_schemas.py           # Schema validation tests
│   └── test_smoke.py             # Basic API health tests
│
├── requirements.txt              # Project dependencies
├── README.md                     # Project documentation
└── .env                          # Environment variables (optional)
```

### Structure Rationale

- **Separation of Concerns**
  - API routes, business logic, data models, and security are split into dedicated modules
  - Improves readability and maintainability

- **Router-Based Design**
  - Endpoints are grouped by domain (auth, properties, analytics)
  - Makes the API easier to extend and test

- **Script Isolation**
  - Data processing is handled outside the main application
  - Prevents heavy computation during runtime

- **Test Organisation**
  - Tests mirror the application structure
  - Ensures full coverage across all components

- **Scalability**
  - Modular layout allows easy addition of new features or services
  - Supports transition to larger systems or microservice architectures

---

Overall, the project structure reflects best practices for FastAPI applications, ensuring clarity, modularity, and ease of future development.

## 11. Installation and Setup

This section provides a step-by-step guide to setting up and running the API locally. The setup process is designed to be reproducible and supports both quick-start execution and full dataset rebuilding.

---

### 11.1 Prerequisites

Before setting up the project, ensure the following are installed:

- Python 3.10 or higher  
- pip (Python package manager)  
- Git (for cloning the repository)  

Optional (for production setup):
- PostgreSQL database  

---

### 11.2 Environment Configuration

The application uses environment variables for configuration.

#### Required Variables

- JWT_SECRET_KEY  
  Secret key used for signing JWT tokens  

#### Optional Variables

- DATABASE_URL  
  Database connection string (defaults to SQLite if not provided)  

- ACCESS_TOKEN_EXPIRE_MINUTES  
  Token expiry duration (default: 60 minutes)  

- ALLOWED_ORIGINS  
  Comma-separated list of allowed CORS origins  

#### Example Configuration

Windows (PowerShell):

```
$env:JWT_SECRET_KEY="your-secret-key"
$env:DATABASE_URL="sqlite:///./app.db"
$env:ACCESS_TOKEN_EXPIRE_MINUTES="60"
```

Linux / macOS:

```
export JWT_SECRET_KEY="your-secret-key"
export DATABASE_URL="sqlite:///./app.db"
export ACCESS_TOKEN_EXPIRE_MINUTES="60"
```

---

### 11.3 Dataset Preparation

The API requires a processed dataset before it can be used.

#### Option A — Quick Start (Recommended)

Use the pre-generated deployment dataset:

```
data/processed/property_records_deploy.csv
```

This option:
- Minimises setup time  
- Is sufficient for testing and demonstration  
- Is used by default in the seeding script  

#### Option B — Rebuild Dataset

To regenerate the dataset from raw files:

1. Ensure required files exist in:

```
data/raw/
data/processed/
```

2. Run the dataset pipeline:

```
python scripts/build_property_dataset.py
```

3. (Optional) Create a smaller deployment dataset:

```
python scripts/make_deploy_dataset.py
```

This will generate:
- property_records.csv (full dataset)  
- property_records_deploy.csv (reduced dataset)  

---

### 11.4 Database Seeding

Once the dataset is prepared, populate the database:

```
python scripts/seed_data.py
```

Key points:
- Loads data into relational tables  
- Uses the deployment dataset by default  
- May take time depending on dataset size (~790k records)  

---

### 11.5 Running the Application

Start the FastAPI development server:

```
uvicorn app.main:app --reload
```

The API will be available at:

- http://127.0.0.1:8000/docs  

---

### 11.6 Verifying Setup

After starting the application:

1. Open /health  
   - Confirms the API is running  

2. Open /docs  
   - Interactive interface for testing endpoints  

3. Test authentication:
   - Register via /auth/register  
   - Login via /auth/login  
   - Use the returned token  

4. Test data access:
   - GET /properties  
   - Access analytics endpoints  

Successful responses confirm:
- Database is correctly seeded  
- Authentication is functioning  
- API endpoints are operational  

---

This setup ensures the API can be reliably deployed and tested locally, while remaining flexible

## 12. API Usage Guide

This section explains how to interact with the API, including authentication, making requests, and using query features such as filtering, pagination, and sorting. The examples reflect the implemented endpoints and behaviour in the current system.

---

### 12.1 Authentication Workflow

Most endpoints require authentication using JWT tokens.

#### Step 1: Register a User

```
POST /auth/register
```
```
Request body:
{
  "username": "demo_user",
  "email": "demo@example.com",
  "password": "Password123!",
  "role": "viewer"
}
```
---

#### Step 2: Login

```
POST /auth/login
```

Form data:
- username
- password
```
Successful response:
{
  "access_token": "<token>",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "demo_user",
    "role": "viewer"
  }
}
```
---

#### Step 3: Use Token

Include the token in request headers:

```
Authorization: Bearer <access_token>
```

This is required for all protected endpoints.

---

### 12.2 Example Requests

#### Retrieve Properties

```
GET /properties
```

Example:
```
GET /properties?limit=10&offset=0
```

---

#### Create Property (Editor/Admin)

```
POST /properties
```
```
Request body:
{
  "price": 250000,
  "postcode": "LS1 1AA",
  "property_type": "F"
}
```
---

#### Update Property

```
PUT /properties/{id}
```

---

#### Delete Property (Admin Only)

```
DELETE /properties/{id}
```

---

#### Analytics Example

```
GET /analytics/price-trend
```

---

### 12.3 Querying and Filtering

The API supports flexible querying using query parameters.

#### Common Filters

- postcode  
- town_city  
- property_type  
- date range  
- energy rating  

Example:
```
GET /properties?town_city=Leeds&property_type=F
```

Multiple filters can be combined:
```
GET /properties?town_city=Leeds&property_type=F&min_price=200000
```

#### Behaviour

- Filters are applied at the database query level  
- Only matching records are returned  
- Invalid filters result in validation errors  

---

### 12.4 Pagination and Sorting

To handle large datasets efficiently, pagination and sorting are supported.

#### Pagination Parameters

- limit → number of records to return  
- offset → starting position  

Example:
```
GET /properties?limit=10&offset=20
```
#### Sorting

Sorting can be applied to supported fields such as:

- price  
- date  
- location  

Example:
```
GET /properties?sort_by=price&order=desc
```

#### Response Structure
```
Paginated responses include metadata:
{
  "total": 1000,
  "limit": 10,
  "offset": 0,
  "items": [...]
}
```
---

This usage guide demonstrates how clients can authenticate, retrieve, and manipulate data using the API while leveraging filtering, pagination, and analytical capabilities.

## 13. API Endpoints Overview

This section provides a structured overview of all available API endpoints. The endpoints are grouped by functionality and follow RESTful conventions with consistent naming and behaviour.

---

### 13.1 Authentication Endpoints

- **POST /auth/register**  
  Register a new user account  
  - Accessible without authentication  
  - Stores user credentials securely (hashed password)  

- **POST /auth/login**  
  Authenticate the user and return the JWT access token  
  - Accepts username/email and password  
  - Returns token for subsequent requests  

- **GET /auth/me**  
  Retrieve details of the currently authenticated user  
  - Requires a valid JWT token  

---

### 13.2 Property Endpoints

- **GET /properties**  
  Retrieve a list of properties  
  - Supports filtering, pagination, and sorting  

- **GET /properties/{id}**  
  Retrieve a specific property by ID  

- **POST /properties**  
  Create a new property record  
  - Requires role: editor or admin  

- **PUT /properties/{id}**  
  Update an existing property  
  - Requires role: editor or admin  

- **DELETE /properties/{id}**  
  Delete a property  
  - Requires role: admin  

---

### 13.3 Energy Certificate Endpoints

- **GET /energy-certificates**  
  Retrieve energy certificate records  

- **POST /energy-certificates**  
  Create a new energy certificate  
  - Requires role: editor or admin  

- **PUT /energy-certificates/{id}**  
  Update an energy certificate  
  - Requires role: editor or admin  

- **DELETE /energy-certificates/{id}**  
  Delete an energy certificate  
  - Requires role: admin  

---

### 13.4 Location Endpoints

- **GET /locations/{postcode}/summary**  
  Retrieve aggregated information for a given location  
  - Includes property statistics and related data  
  - May include links to related resources (HATEOAS-style)  

---

### 13.5 Analytics Endpoints

- **GET /analytics/price-trend**  
  Returns property price trends over time  

- **GET /analytics/energy-price-impact**  
  Analyses the relationship between energy efficiency and price  

- **GET /analytics/top-areas**  
  Identifies areas with the highest average property prices  

- **GET /analytics/epc-distribution**  
  Provides distribution of EPC ratings  

---
### 13.6 Service Endpoints

- **GET /info**  
  Returns metadata about the API (version, description, available features)

- **GET /health**  
  Returns API health status

All endpoints return JSON responses and follow standard HTTP status codes. Protected endpoints require a valid JWT token and enforce role-based access control.

## 14. Testing Strategy

The API includes a comprehensive automated testing suite implemented using Pytest. The testing strategy is designed to validate functionality, ensure correctness, enforce security constraints, and verify behaviour under both normal and edge-case scenarios.

---

### 14.1 Testing Approach

Testing is performed at the **API level** using HTTP requests rather than isolated unit tests. This ensures that the system is tested as a complete web service, covering:

- Request validation (input schemas)
- Routing and endpoint behaviour
- Business logic execution
- Database interactions
- Authentication and authorization

Each test verifies:
- Correct HTTP status codes (e.g. 200, 201, 400, 401, 403, 404)
- Expected JSON response structure
- Proper enforcement of access control
- Handling of invalid inputs and edge cases

This approach ensures realistic testing conditions that closely match actual API usage.

---

### 14.2 Test Architecture

The test suite is structured to ensure isolation, reproducibility, and consistency.

Key components:

- **Isolated Test Database**
  - Uses SQLite for testing
  - Separate from the development database
  - Prevents interference with real data  

- **Dependency Overrides**
  - FastAPI dependency injection is overridden to use test database sessions  
  - Ensures all requests operate within the test environment  

- **Transactional Testing**
  - Each test runs in isolation  
  - Database state is reset between tests  

- **Fixtures**
  - Reusable fixtures defined in `conftest.py`  
  - Provide:
    - Test client  
    - Sample users (viewer, editor, admin)  
    - Authentication tokens  
    - Sample property and EPC data  

This architecture ensures reliable and repeatable test execution.

---

### 14.3 Test Coverage

The test suite provides broad coverage across all major components of the API:

#### Authentication
- User registration and login  
- JWT token generation and validation  
- Invalid credentials handling  
- Role enforcement  
- Inactive user restrictions  

#### Properties
- CRUD operations (create, retrieve, update, delete)  
- Filtering, sorting, and pagination  
- Validation of inputs and query parameters  
- Duplicate handling and error cases  

#### Energy Certificates
- CRUD operations  
- Validation of relationships with properties  
- Duplicate EPC handling  
- Role-based access restrictions  

#### Analytics
- Aggregation endpoints (e.g. averages, trends)  
- Data grouping and filtering  
- Handling of missing or insufficient data  

#### Locations
- Location summary endpoints  
- Validation of postcode-based queries  
- Inclusion of related resource links  

#### Security
- Authentication enforcement (401 errors)  
- Authorization enforcement (403 errors)  
- Token validation and access control  

#### Schemas
- Input validation using Pydantic  
- Boundary testing (e.g. invalid values, missing fields)  

#### Smoke Tests
- API startup validation  
- `/health` endpoint availability  
- OpenAPI and documentation endpoints  

---

### 14.4 Running Tests

To execute all tests:

```
pytest -v
```

To run a specific test file:

```
pytest tests/test_properties.py -v
```

Test results include:
- Pass/fail status for each test  
- Detailed error messages for failed cases  

---

### 14.5 Testing Justification

The chosen testing strategy is appropriate for this project because:

- **End-to-End Validation**  
  Testing at the API level ensures all components (routing, validation, database, security) work together correctly  

- **High Coverage of Core Features**  
  All major functionalities, including CRUD operations and analytics, are tested  

- **Security Assurance**  
  Authentication and role-based access control are thoroughly validated  

- **Reliability and Maintainability**  
  Use of fixtures and isolated environments ensures tests are reproducible and easy to maintain  

- **Alignment with Real Usage**  
  Tests simulate real client interactions, improving confidence in production readiness  

---

Overall, the testing strategy ensures that the API is robust, secure, and reliable, meeting the requirements of the coursework and supporting production-ready behaviour.

## 15. Security Considerations

The API incorporates several security mechanisms to ensure safe and controlled access:

- **JWT-Based Authentication**
  - Stateless authentication using signed tokens
  - Tokens include expiry to reduce the risk of misuse  

- **Password Security**
  - Passwords are hashed before storage  
  - Plaintext passwords are never stored  

- **Role-Based Access Control (RBAC)**
  - viewer → read-only  
  - editor → create/update  
  - admin → full access  
  - Enforced at the endpoint level  

- **Input Validation**
  - All incoming data is validated using Pydantic  
  - Prevents malformed or invalid data  

- **Error Handling**
  - Controlled error responses avoid leaking sensitive information  

- **Environment Variables**
  - Secrets (e.g. JWT key) are not hardcoded  
  - Improves security for deployment  

---

## 16. Performance and Scalability

The system is designed to handle relatively large datasets efficiently while remaining scalable:

- **Efficient Querying**
  - Filtering, pagination, and sorting reduce data load per request  

- **Indexing**
  - Frequently queried fields (postcode, price, date) are indexed  

- **Preprocessed Data**
  - Data cleaning and merging are performed offline  
  - Reduces runtime computation  

- **Database Flexibility**
  - SQLite for development  
  - PostgreSQL for production scalability  

- **Stateless API**
  - Enables horizontal scaling (multiple instances)  

- **Deployment Dataset**
  - Smaller dataset improves performance during testing and deployment  

---

## 17. Deployment

The API is designed for both local development and production deployment.

---

### 17.1 Local Deployment

Steps:

1. Configure environment variables  
2. Prepare dataset  
3. Seed database  
4. Run server:

```
uvicorn app.main:app --reload
```

Access:
- http://127.0.0.1:8000/docs  
- http://127.0.0.1:8000/health  

---

### 17.2 Production Deployment

For production environments:

- Use **PostgreSQL** instead of SQLite  
- Set environment variables securely  
- Run using a production ASGI server (e.g. Uvicorn with workers)  
- Deploy on cloud platforms (e.g. AWS, Azure, Render)  

Optional improvements:
- Enable HTTPS  
- Add logging and monitoring  
- Use containerisation (Docker)  

---

### 17.3 Environment Configuration

Deployment is controlled via environment variables:

- `DATABASE_URL` → database connection  
- `JWT_SECRET_KEY` → token signing  
- `ACCESS_TOKEN_EXPIRE_MINUTES` → token expiry  
- `ALLOWED_ORIGINS` → CORS configuration  

This ensures flexibility across environments without code changes.

---

## 18. Design Decisions and Justification

Key design decisions include:

- **FastAPI Framework**
  - Chosen for performance and automatic documentation  

- **SQLAlchemy ORM**
  - Provides structured and flexible database interaction  

- **JWT Authentication**
  - Enables stateless and scalable security  

- **Role-Based Access Control**
  - Demonstrates secure and controlled data access  

- **Preprocessing Pipeline**
  - Separates data preparation from runtime logic  
  - Improves performance and maintainability  

- **Analytics Endpoints**
  - Extend beyond CRUD to provide meaningful insights  

These decisions ensure the API is both practical and aligned with RESTful design principles.

---

## 19. Limitations

- Some EPC data may be incomplete or unmatched  
- Large datasets increase initial seeding time  
- SQLite is not suitable for high-concurrency production use  
- No frontend interface is included  
- Analytics are limited to descriptive insights  

---

## 20. Future Improvements

- Implement refresh tokens for improved authentication  
- Add caching for analytics endpoints  
- Improve EPC matching accuracy  
- Enhance filtering and search capabilities  
- Deploy using a managed cloud database  
- Add rate limiting and monitoring  
- Extend analytics with machine learning models  

## 21. Generative AI Usage Declaration
Generative AI tools were used during the development of this project to support specific aspects of implementation and documentation. Their use was limited to assistance and did not replace independent understanding or decision-making.

### Areas of Assistance

- **Code Support**
  - Debugging and resolving implementation issues  
  - Suggesting improvements to structure and readability  
  - Assisting with best practices in FastAPI and SQLAlchemy  

- **Documentation**
  - Structuring and refining the README  
  - Improving clarity and organisation of technical explanations  

- **Concept Clarification**
  - Reinforcing understanding of RESTful API design  
  - Assisting with authentication and testing strategies  

### Verification and Original Work

- All generated content was **reviewed, validated, and adapted**  
- The final implementation reflects **independent development and understanding**  
- No AI-generated content was used without verification  

### Compliance

The use of generative AI in this project complies with university guidelines. AI tools were used as a **supporting aid**, and all submitted work represents the student’s own effort and understanding.
