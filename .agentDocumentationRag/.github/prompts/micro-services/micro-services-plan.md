# Microservices Migration Plan for Chinese Auction System

## Overview

This plan transforms the monolithic Chinese Auction application into a microservices architecture to showcase modern distributed system patterns, improve scalability, and create a strong portfolio piece. The approach prioritizes learning value while staying practical for implementation.

## Goals
- **Learning**: Demonstrate microservices patterns (API Gateway, event-driven architecture, distributed state)
- **Portfolio**: Showcase modern cloud-native architecture skills
- **Scalability**: Enable independent scaling of services during peak raffle loads

## Target Architecture

### Service Decomposition
1. **Auth Service** - User authentication, JWT token generation, user management
2. **Catalog Service** - Gifts, categories, donor management
3. **Purchase Service** - Shopping cart, purchase workflow, order history
4. **Raffle Service** - Winner selection, raffle state management, winning records
5. **Notification Service** - Email notifications for winners and donors
6. **API Gateway** - Single entry point, routing, authentication validation

### Service Data Store Decisions
For each microservice we recommend a primary data store choice. These are suggestions based on typical patterns; adjust to your operational constraints.

- Auth Service: Relational (PostgreSQL / SQL Server)
   - Rationale: User data and roles are relational and require ACID guarantees for updates (role changes, user management). Relational DBs simplify queries for user lookups and joins.

- Catalog (Gift) Service: Relational (PostgreSQL / SQL Server)
   - Rationale: Catalog entities (gifts, categories, donors) are structured and often require joins, filtering, and transactional updates. Use relational DB for data integrity and complex queries. Consider a read-optimized replica or materialized views for public reads.

- Purchase Service: Relational (PostgreSQL / SQL Server)
   - Rationale: Purchases, cart items, and transactions benefit from ACID semantics. Denormalize gift snapshot fields into purchases for historical accuracy. Relational DB facilitates reporting and joins for order history.

- Raffle Service: Relational (PostgreSQL / SQL Server) + Redis for state
   - Rationale: Winning records and raffle history should be stored relationally. Raffle runtime state (Open/Finished) is ephemeral and should be stored in Redis for fast access and pub/sub notifications.

- Notification Service: Non-relational / Message-driven (no dedicated DB) or lightweight store
   - Rationale: Notifications are event-driven; durable queue (RabbitMQ) and optional lightweight store (NoSQL like MongoDB) for history/archive. Many implementations don't require a primary DB; use message queues and object storage for attachments.

- API Gateway: No DB (stateless) or lightweight config store
   - Rationale: Gateway should be stateless. Use configuration management (consul/etcd) or DB only if you need dynamic routing stored centrally.

- Read-models / Materialized Views (optional): Non-relational (Elasticsearch / MongoDB / Redis) for fast queries and dashboards
   - Rationale: For donor dashboards and analytic queries, maintain denormalized read models in a NoSQL store or search index optimized for the query patterns.


### Communication Patterns
- **Synchronous**: HTTP/REST via API Gateway for user-facing operations
- **Asynchronous**: RabbitMQ for events (WinnerSelected, PurchaseCompleted, RaffleExecuted)
- **State Management**: Redis for distributed raffle state (Open/Finished)
- **File Storage**: Centralized blob storage (MinIO/Azure Blob) for gift images

## Implementation Phases

### Phase 1: Infrastructure Setup

#### 1.1 Set up shared infrastructure components
- **Docker Compose**: Create `docker-compose.yml` for local development environment
  - PostgreSQL/SQL Server containers for each service database
  - Redis container for distributed caching and state
  - RabbitMQ container with management UI
  - MinIO container for S3-compatible object storage
  - Seq container for centralized logging

- **File**: Create `docker-compose.yml` at solution root
- **File**: Create `.env` file for shared configuration (passwords, ports)

#### 1.2 Create API Gateway project
- **Tool**: `dotnet new web -n ApiGateway`
- **Package**: Install `Yarp.ReverseProxy` NuGet package
- **Configuration**: 
  - Create `appsettings.json` with route definitions
  - Configure CORS for Angular client
  - Set up JWT authentication middleware
  - Define routes for each microservice

**Current Reference**: See `server/Program.cs` for existing CORS and auth setup

---

### Phase 2: Extract Simple Services (Learn Patterns)

#### 2.1 Extract Notification Service
**Purpose**: Easiest service to extract - no dependencies, purely reactive

**Steps**:
1. Create new ASP.NET Core project: `NotificationService`
2. Move components from monolith:
   - `Services/EmailService.cs` → `NotificationService/Services/EmailService.cs`
   - `Controllers/EmailController.cs` → `NotificationService/Controllers/EmailController.cs`
   - SMTP configuration from `appsettings.json`

3. Implement RabbitMQ consumer:
   - Install `RabbitMQ.Client` package
   - Create `WinnerNotificationConsumer` background service
   - Subscribe to `winner.selected` queue
   - Process events asynchronously

4. Create event DTOs:
   ```csharp
   WinnerSelectedEvent {
       WinnerId, WinnerEmail, WinnerFullName,
       GiftId, GiftName, CategoryName,
       DonorName, DonorEmail
   }
   ```

**Testing**:
- Unit tests: Email template generation
- Integration tests: RabbitMQ message consumption
- Manual test: Publish test message, verify email sent

**Current References**:
- `server/Services/EmailService.cs`
- `server/Controllers/EmailController.cs`
- `server/appsettings.json` (Email configuration)

#### 2.2 Extract Auth Service
**Purpose**: Critical foundational service - all others depend on it

**Steps**:
1. Create project: `AuthService`
2. Move components:
   - `Controllers/AuthController.cs`
   - `Controllers/UserController.cs`
   - `Services/AuthService.cs`
   - `Services/UserService.cs`
   - `Services/JwtService.cs`
   - `Repositories/UserRepository.cs`
   - `Models/UserModel.cs`
   - `DTOs/AuthDto.cs`, `DTOs/UserDto.cs`
   - `Mappings/UserProfile.cs`

3. Create `AuthDbContext` with only `Users` table
4. Configure JWT token generation (keep same secret for compatibility)
5. Implement endpoints:
   - POST `/api/auth/register`
   - POST `/api/auth/login`
   - GET `/api/users/{id}`
   - GET `/api/users` (for internal service calls)
   - PUT `/api/users/{id}/role`

6. Add API client interface for other services to consume

**Testing**:
- Integration tests: Register, login, get user
- JWT validation test
- Role assignment test

**Current References**:
- `server/Controllers/AuthController.cs`
- `server/Services/AuthService.cs`
- `server/Services/JwtService.cs`
- `server/Data/AppDbContext.cs` (UserModel configuration)

---

### Phase 3: Extract Core Business Services

#### 3.1 Extract Gift Catalog Service
**Purpose**: Manage gifts, categories, and donor information

**Steps**:
1. Create project: `CatalogService`
2. Move components:
   - `Controllers/GiftController.cs`
   - `Controllers/CategoryController.cs`
   - `Controllers/DonorController.cs`
   - `Services/GiftService.cs`, `Services/CategoryService.cs`, `Services/DonorService.cs`
   - `Repositories/GiftRepository.cs`, `Repositories/CategoryRepository.cs`
   - `Models/GiftModel.cs`, `Models/CategoryModel.cs`
   - `DTOs/GiftDto.cs`, `DTOs/CategoryDto.cs`, `DTOs/DonorDto.cs`
   - `Mappings/GiftProfile.cs`, `Mappings/CategoryProfile.cs`, `Mappings/DonorProfile.cs`

3. **Handle Donor Data** (denormalization):
   - Store basic donor info (Id, Name, Email, City) in `CatalogDB`
   - Subscribe to `user.role.changed` events from Auth Service
   - When user promoted to Donor role, cache their info locally
   - Call Auth Service API to get donor details when needed

4. **Update Gift Image Storage**:
   - Replace `wwwroot/uploads/gifts` with blob storage client
   - Upload to MinIO/Azure Blob on gift creation
   - Return blob URL in gift DTOs

5. **Publish Events**:
   - `gift.created` when new gift added
   - `gift.updated` when gift details change
   - `gift.deleted` when gift removed

6. **Implement Donor Dashboard**:
- Current `DonorService.GetDonorDashboard()` queries across multiple entities
- Options:
  - **A) Read Model**: Subscribe to events from Purchase/Raffle services, build local materialized view
  - **B) API Orchestration**: Call Purchase Service and Raffle Service APIs to aggregate data
- **Recommendation**: Start with (B) for simplicity, move to (A) if performance issues

**Testing**:
- CRUD operations for gifts and categories
- Image upload to blob storage
- Donor dashboard data aggregation
- Event publishing verification

**Current References**:
- `server/Controllers/GiftController.cs`
- `server/Services/GiftService.cs`
- `server/Repositories/GiftRepository.cs`
- `server/Services/DonorService.cs` (complex dashboard query)

#### 3.2 Extract Purchase Service
**Purpose**: Shopping cart and purchase workflow management

**Steps**:
1. Create project: `PurchaseService`
2. Move components:
   - `Controllers/CartController.cs`
   - `Controllers/PurchaseController.cs`
   - `Services/CartService.cs`
   - `Services/PurchaseService.cs`
   - `Repositories/PurchaseRepository.cs`
   - `Models/PurchaseModel.cs`
   - `DTOs/CartDto.cs`, `DTOs/PurchaseDto.cs`
   - `Mappings/PurchaseProfile.cs`

3. **Handle Gift References**:
   - Remove navigation property `Purchase.Gift`
   - Store `GiftId`, `GiftName`, `GiftPrice`, `GiftImageUrl` directly in Purchase table (denormalization)
   - On cart add: Call Catalog Service API to validate gift exists and get snapshot
   - On purchase list: Return cached gift data (no additional calls)

4. **Handle Raffle State Dependency**:
   - Remove singleton `RaffleStateService`
   - Use Redis client to check raffle state before cart operations
   - Subscribe to Redis Pub/Sub channel `raffle.state.changed`
   - Cache state locally with invalidation on event

5. **Publish Events**:
   - `purchase.completed` when checkout finishes
   - Include: PurchaseId, UserId, GiftId, Quantity, TotalAmount

6. **Implement Endpoints**:
   - Shopping cart: GET, POST, PUT, DELETE
   - Checkout: POST `/api/cart/checkout`
   - Purchase history: GET `/api/purchases` (by user)
   - Purchase statistics: GET `/api/purchases/gift/{giftId}/count`

**Testing**:
- Add to cart, update quantity, remove item
- Checkout flow
- Raffle state validation (should block checkout when raffle finished)
- Event publishing

**Current References**:
- `server/Controllers/CartController.cs`
- `server/Services/CartService.cs`
- `server/Services/RaffleStateService.cs` (singleton to replace)

#### 3.3 Extract Raffle Service
**Purpose**: Execute raffles, select winners, manage raffle state

**Steps**:
1. Create project: `RaffleService`
2. Move components:
   - `Controllers/WinningController.cs`
   - `Services/WinningService.cs`
   - `Repositories/WinningRepository.cs`
   - `Models/WinningModel.cs`
   - `DTOs/WinningDto.cs`
   - `Mappings/WinningProfile.cs`

3. **Replace Singleton State with Redis**:
   - Use Redis key `raffle:state` with values "Open"/"Finished"
   - GET `/api/raffle/state` reads from Redis
   - POST `/api/raffle/finish` updates Redis and publishes to Pub/Sub
   - Set TTL or persist based on business requirements

4. **Orchestrate Raffle Execution**:
   
   Current monolith raffle logic:
   - Query all completed purchases from DB
   - Group by gift
   - Random winner selection
   - Create winning records
   - Update gift.HasWinning flag
   - Send email notifications
   
   New distributed logic:
   - Call Purchase Service API: GET `/api/purchases/completed` → list of all completed purchases
   - Group locally by GiftId
   - Random winner selection (same algorithm)
   - Create winning records in `RaffleDB`
   - Publish events for each winner:
     - `winner.selected` → RabbitMQ (consumed by Notification Service)
     - `gift.winner.assigned` → RabbitMQ (consumed by Catalog Service to update flag)
   - Update raffle state in Redis to "Finished"
   - Publish `raffle.state.changed` event to Redis Pub/Sub

5. **Handle Transactions** (Critical Decision):
   - **Monolith**: Single DB transaction ensures atomicity
   - **Microservices Options**:
     - **A) Eventual Consistency**: Accept that notifications might fail, gifts might not update immediately
     - **B) Saga Pattern**: Orchestration with compensating transactions on failure
     - **C) Event Sourcing**: Store events, rebuild state from event log
   - **Recommendation**: Start with (A) - use transactional outbox pattern for reliable event publishing

6. **Implement Endpoints**:
   - POST `/api/raffle/execute` - Run raffle for all gifts
   - POST `/api/raffle/execute/{giftId}` - Run raffle for specific gift
   - GET `/api/raffle/state` - Check if raffle is open/finished
   - POST `/api/raffle/finish` - Mark raffle as finished (prevent new purchases)
   - GET `/api/winnings` - List all winners
   - GET `/api/winnings/search` - Search and filter winners

**Testing**:
- Execute raffle, verify winners selected randomly
- Verify events published to RabbitMQ
- Verify state change in Redis propagates
- Test rollback/compensation on failure
- Verify Purchase Service blocks operations after raffle finished

**Current References**:
- `server/Services/WinningService.cs` (complex transaction logic)
- `server/Controllers/WinningController.cs`

---

### Phase 4: Handle Cross-Cutting Concerns

#### 4.1 Implement service-to-service communication

1. **Create Shared Library**: `Common.Infrastructure`
   - HTTP client factory with Polly policies
   - Retry policy: 3 attempts with exponential backoff
   - Circuit breaker: Open after 5 failures, half-open after 30s
   - Timeout: 10s per request

2. **Service Discovery** (choose one):
   - **Simple**: Configuration-based URLs in appsettings
   - **Consul**: Service registration and discovery
   - **Kubernetes**: Service DNS

3. **Distributed Tracing**:
   - Add correlation ID middleware to each service
   - Pass `X-Correlation-ID` header in all service-to-service calls
   - Log correlation ID with every log entry
   - Configure OpenTelemetry for observability

4. **Create Service Clients**:
   - `IAuthServiceClient` - used by all services to validate users
   - `ICatalogServiceClient` - used by Purchase Service to get gift info
   - `IPurchaseServiceClient` - used by Raffle Service to get purchases
   - Use `IHttpClientFactory` with named clients

#### 4.2 Address data consistency challenges

1. **Donor Dashboard** (most complex query):
   - Current: Joins Users, Gifts, Purchases, Winnings in one query
   - Solution: Build read model in Catalog Service
     - Subscribe to events: `purchase.completed`, `winner.selected`
     - Store aggregated statistics in separate table: `DonorStatistics`
     - Fields: DonorId, GiftsCount, TicketsSold, UniqueBuyers, WinningsCount
     - Update incrementally on each event
     - Rebuild from scratch if out of sync (eventual consistency)

2. **User Deletion**:
   - Current: Cascade delete purchases, restrict if user is donor with gifts
   - Solution: Distributed saga
     - Auth Service receives delete request
     - Check role (call Catalog Service to check if donor has gifts)
     - If donor with gifts, reject
     - Otherwise, publish `user.delete.requested` event
     - Purchase Service listens and deletes/anonymizes purchases
     - Auth Service listens for `purchases.deleted.confirmed`
     - Auth Service deletes user record
     - Publish `user.deleted` event

3. **Gift Snapshot in Purchases**:
   - Store gift details (name, price, image URL) in Purchase table at time of purchase
   - Protects against gift changes/deletions
   - Trade-off: Data duplication vs. historical accuracy

#### 4.3 Configure API Gateway routing
File: `ApiGateway/appsettings.json`

```json
{
  "ReverseProxy": {
 "Routes": {
   "auth-route": {
     "ClusterId": "auth-cluster",
     "Match": { "Path": "/api/auth/{**catch-all}" }
   },
   "users-route": {
     "ClusterId": "auth-cluster",
     "Match": { "Path": "/api/users/{**catch-all}" },
     "AuthorizationPolicy": "Admin"
   },
   "gifts-route": {
     "ClusterId": "catalog-cluster",
     "Match": { "Path": "/api/gifts/{**catch-all}" }
   },
   "categories-route": {
     "ClusterId": "catalog-cluster",
     "Match": { "Path": "/api/categories/{**catch-all}" }
   },
   "donors-route": {
     "ClusterId": "catalog-cluster",
     "Match": { "Path": "/api/donors/{**catch-all}" }
   },
   "cart-route": {
     "ClusterId": "purchase-cluster",
     "Match": { "Path": "/api/cart/{**catch-all}" },
     "AuthorizationPolicy": "Authenticated"
   },
   "purchases-route": {
     "ClusterId": "purchase-cluster",
     "Match": { "Path": "/api/purchases/{**catch-all}" },
     "AuthorizationPolicy": "Authenticated"
   },
   "raffle-route": {
     "ClusterId": "raffle-cluster",
     "Match": { "Path": "/api/raffle/{**catch-all}" },
     "AuthorizationPolicy": "Admin"
   },
   "winnings-route": {
     "ClusterId": "raffle-cluster",
     "Match": { "Path": "/api/winnings/{**catch-all}" }
   }
 },
 "Clusters": {
   "auth-cluster": {
     "Destinations": {
       "auth-service": { "Address": "http://auth-service:5001" }
     }
   },
   "catalog-cluster": {
     "Destinations": {
       "catalog-service": { "Address": "http://catalog-service:5002" }
     }
   },
   "purchase-cluster": {
     "Destinations": {
       "purchase-service": { "Address": "http://purchase-service:5003" }
     }
   },
   "raffle-cluster": {
     "Destinations": {
       "raffle-service": { "Address": "http://raffle-service:5004" }
     }
   }
 }
  }
}
```

---

### Phase 5: Migration & Data

#### 5.1 Migrate database to service-specific databases
**Strategy**: Database-per-service pattern for true independence

1. **Create Databases**:
   - `AuthDB` - Users table only
   - `CatalogDB` - Gifts, Categories, DonorCache tables
   - `PurchaseDB` - Purchases table (with denormalized gift fields)
   - `RaffleDB` - Winnings table
   - `NotificationDB` (optional) - Email audit logs

2. **Migration Scripts**:
   - Export data from monolith `AppDbContext`
   - Split by domain entity
   - Import into new service databases
   - Handle foreign key breakage:
     - Remove navigation properties
     - Keep only ID references
     - Denormalize where needed

3. **EF Core Migrations**:
   - Create `DbContext` for each service
   - Run migrations: `dotnet ef migrations add InitialCreate`
   - Update connection strings in each service

4. **Backward Compatibility** (during migration):
   - Keep monolith running
   - New writes go to microservices
   - Sync back to monolith DB for old services
   - Gradually cutover traffic via API Gateway routing

**Current Reference**: `server/Data/AppDbContext.cs` for entity configurations

#### 5.2 Update Angular client
**Changes**: Point to API Gateway instead of direct backend

1. **Update Environment Files**:
   - `client/src/environments/environment.ts`
   - Change `apiUrl: 'http://localhost:5000'` to `apiUrl: 'http://localhost:8080'` (Gateway)

2. **No Service Changes Needed**:
   - All HTTP services already use relative paths
   - API Gateway routes to correct microservices
   - Response DTOs remain unchanged

3. **Handle New Error Patterns**:
   - Service unavailable (503) if microservice is down
   - Circuit breaker open responses
   - Add retry logic for transient failures

**Current References**:
- Angular services in `client/src/app/`

---

### Phase 6: Deployment & DevOps

#### 6.1 Containerize each service

1. **Create Dockerfiles** for each service:
   ```dockerfile
   FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
   WORKDIR /app
   EXPOSE 80
   
   FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
   WORKDIR /src
   COPY ["ServiceName/ServiceName.csproj", "ServiceName/"]
   RUN dotnet restore "ServiceName/ServiceName.csproj"
   COPY . .
   WORKDIR "/src/ServiceName"
   RUN dotnet build "ServiceName.csproj" -c Release -o /app/build
   
   FROM build AS publish
   RUN dotnet publish "ServiceName.csproj" -c Release -o /app/publish
   
   FROM base AS final
   WORKDIR /app
   COPY --from=publish /app/publish .
   ENTRYPOINT ["dotnet", "ServiceName.dll"]
   ```

2. **Update docker-compose.yml** to include all services:
   - auth-service
   - catalog-service
   - purchase-service
   - raffle-service
   - notification-service
   - api-gateway
   - postgres (or SQL Server)
   - redis
   - rabbitmq
   - minio
   - seq

3. **Environment Variables**:
   - Databaction strings
   - RabbitMQ connection
   - Redis connection
   - JWT secret (shared)
   - SMTP credentials

#### 6.2 Set up CI/CD pipeline (Optional - Portfolio Enhancement)
**Platform**: GitHub Actions (already have `.github` folder)

1. **Per-Service Pipelines**:
   - `.github/workflows/auth-service.yml`
   - `.github/workflows/catalog-service.yml`
   - etc.

2. **Pipeline Steps**:
   - Trigger: On push to `main` with changes in service folder
   - Build: `dotnet build`
   - Test: `dotnet test`
   - Docker Build: `docker build -t service:version`
   - Push: To Docker Hub or Azure Container Registry
   - Deploy: To Kubernetes cluster or Azure App Service

3. **Deployment Target Options**:
   - **Local**: Docker Compose (simplest)
   - **Azure**: AKS (Azure Kubernetes Service) + Azure Service Bus
   - **AWS**: EKS + SQS/SNS
   - **Self-Hosted**: Kubernetes with MetalLB

---

## Verification & Testing

### Unit Tests
- Migrate existing tests from `SERVER.Tests/` to each service project
- Each service has its own test project: `AuthService.Tests`, `CatalogService.Tests`, etc.
- Mock HTTP clients for service-to-service calls
- Mock RabbitMQ/Redis for integration points

### Integration Tests
1. **TestContainers**: Spin up real dependencies (postgres, redis, rabbitmq)
2. **Test Scenarios**:
   - Auth Service: Register → Login → Get JWT
   - Catalog Service: Create gift → Upload image → Retrieve gift
   - Purchase Service: Add to cart → Checkout → Verify purchase record
   - Raffle Service: Execute raffle → Verify winners created → Verify events published
   - Notification Service: Consume event → Verify email sent (mock SMTP)

### End-to-End Tests
**Full workflow**:

1. User registers (Auth Service)
2. Donor adds gift (Catalog Service)
3. User browses gifts (Catalog Service)
4. User adds gift to cart (Purchase Service)
5. User checks out (Purchase Service)
6. Admin finishes raffle state (Raffle Service)
7. Admin executes raffle (Raffle Service)
8. Verify winner record created (Raffle Service)
9. Verify email sent (Notification Service)
10. Verify purchase blocked after raffle (Purchase Service)

**Tools**:
- Postman/Newman for API testing
- Playwright/Cypress for UI testing through Angular client
- k6 for load testing

### Performance Testing
1. **Load Test Raffle Execution**:
   - Scenario: 1000 gifts, 10,000 purchases
   - Execute raffle via API
   - Measure: Completion time, memory usage, event throughput
   - Target: Complete within 30 seconds

2. **Load Test Purchase Checkout**:
   - Scenario: 100 concurrent users checking out
   - Measure: Response time, error rate
   - Verify: Circuit breakers activate appropriately

### Resilience Testing
1. **Chaos Engineering**:
   - Kill Notification Service → Raffle should still succeed
   - Kill Catalog Service → Purchase Service should fail gracefully
   - Introduce network latency → Verify timeouts and retries work

2. **Redis Failure**:
   - Stop Redis → Verify services handle gracefully
   - Start Redis → Verify state recovers

3. **RabbitMQ Failure**:
   - Stop RabbitMQ → Verify producers handle connection loss
   - Start RabbitMQ → Verify messages are redelivered

---

## Key Decisions & Trade-offs

### 1. Service Boundaries
**Decision**: Domain-driven boundaries (Auth, Catalog, Purchase, Raffle, Notification)  
**Alternative**: Technical layers (API, Business Logic, Data Access) or feature-based  
**Rationale**: Domain boundaries maximize business value isolation, enable independent team ownership, and align with bounded contexts in DDD

### 2. Data Consistency
**Decision**: Eventual consistency with event-driven synchronization  
**Alternative**: Distributed transactions (2PC, Saga)  
**Rationale**: Accepting eventual consistency trades strong consistency for availability and scalability. For this domain (raffle system), slight delays in donor statistics or email delivery are acceptable. Critical operations (purchase validation) use synchronous calls.

### 3. Communication Pattern
**Decision**: Event-driven (RabbitMQ) for notifications, synchronous HTTP for user-facing operations  
**Alternative**: All async (event sourcing), all sync (REST only)  
**Rationale**: Hybrid approach balances complexity and user experience. Users expect immediate feedback for cart operations (sync), but email notifications can be delayed (async).

### 4. Raffle State Management
**Decision**: Redis-backed distributed state with Pub/Sub  
**Alternative**: Database polling, etcd, Zookeeper  
**Rationale**: Redis provides low-latency reads for "check raffle state" queries (frequent operation), Pub/Sub enables real-time invalidation without polling. Simpler than coordination services like etcd.

### 5. Donor Dashboard
**Decision**: Build read model with event sourcing  
**Alternative**: Real-time API orchestration  
**Rationale**: Dashboard queries aggregate data from 4 services. Event-sourced read model trades consistency for performance - dashboard shows slightly stale data but responds instantly. Admin use case tolerates eventual consistency.

### 6. Gift Data in Purchases
**Decision**: Denormalize gift snapshot in Purchase table  
**Alternative**: Store only GiftId, query Catalog Service on every read  
**Rationale**: Historical accuracy matters - purchases should show gift details at time of purchase, even if gift later changes. Reduces service coupling and Catalog Service load. Trade-off: data duplication vs. query performance.

### 7. API Gateway
**Decision**: YARP (Yet Another Reverse Proxy)  
**Alternative**: Ocelot, Kong, Envoy, Istio service mesh  
**Rationale**: YARP is .NET-native with excellent integration (same ecosystem), simpler than service mesh for this scale. Strong routing, authentication, and load balancing features. Good learning curve for beginners.

### 8. Database Strategy
**Decision**: Database-per-service  
**Alternative**: Shared database with schema-per-service  
**Rationale**: True decoupling enables independent schema changes, migrations, and technology choices. Required for independent deployments. Trade-off: Cross-service queries require aggregation patterns, increased complexity.

### 9. Transaction Handling
**Decision**: Transactional outbox pattern for reliable event publishing  
**Alternative**: Saga orchestration, 2-phase commit  
**Rationale**: Outbox ensures events published exactly-once even if message broker is down. Simpler than saga for this use case. Raffle execution writes winning records and events in same DB transaction, background worker publishes from outbox table.

### 10. Migration Strategy
**Decision**: Incremental (Strangler Fig pattern)  
**Alternative**: Big-bang rewrite  
**Rationale**: Reduces risk - services can be extracted one-by-one, tested, and rolled back if issues arise. Allows learning progressively. API Gateway enables gradual traffic cutover.

---

## Success Metrics

### Technical Metrics
- **Service Independence**: Each service deploys without affecting others
- **Scalability**: Purchase Service scales independently during high-traffic periods
- **Resilience**: System survives Notification Service failure with zero raffle impact
- **Performance**: Raffle execution completes in <30s for 10K purchases

### Learning Outcomes
- Hands-on experience with: Docker, Kubernetes, RabbitMQ, Redis, API Gateway
- Understanding of: Eventual consistency, event-driven architecture, distributed tracing, saga pattern
- Portfolio demonstration: Production-ready microservices architecture

### Portfolio Value
- GitHub repo showcasing: Architecture diagrams, Docker Compose setup, multi-service deployment
- Technical blog posts: "Migrating a Monolith to Microservices", "Handling Distributed Transactions"
- Resume bullet: "Architected and implemented microservices migration for auction platform handling 10K+ concurrent users"

---

## Resources & Further Reading

### Books
- *Building Microservices* by Sam Newman
- *Microservices Patterns* by Chris Richardson
- *Domain-Driven Design* by Eric Evans

### Documentation
- YARP: https://microsoft.github.io/reverse-proxy/
- RabbitMQ: https://www.rabbitmq.com/getstarted.html
- Docker Compose: https://docs.docker.com/compose/

### Patterns
- Strangler Fig: https://martinfowler.com/bliki/StranglerFigApplication.html
- Saga Pattern: https://microservices.io/patterns/data/saga.html
- Transactional Outbox: https://microservices.io/patterns/data/transactional-outbox.html

---

## Next Steps

1. **Review & Approve This Plan**: Ensure alignment on approach and priorities
2. **Set Up Infrastructure**: Start with Phase 1 - Docker Compose environment
3. **Extract First Service**: Begin with Notification Service (simplest)
4. **Iterate**: Extract one service at a time, test thoroughly, learn and adjust
5. **Document Journey**: Keep notes for blog posts and portfolio presentation

Ready to begin implementation? Start with Phase 1: Infrastructure Setup.

