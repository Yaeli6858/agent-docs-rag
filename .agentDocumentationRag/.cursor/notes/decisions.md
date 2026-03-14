# Technical Decisions — Chinese Auction System

## Database
- Chose SQL Server with Entity Framework Core for relational data
- Repositories must NOT map to DTOs — mapping is Service responsibility
- Use async EF Core APIs only (ToListAsync, FirstOrDefaultAsync)

## Security
- JWT authentication for all protected endpoints
- Extract user identity from token claims when it needed in backend logic
- Never accept user ID or role from client input
- Example: User.FindFirst(ClaimTypes.NameIdentifier)

## Logging
- Serilog chosen for structured logging
- Use structured format: logger.LogInformation("Processed {GiftId}", id)
- Never log secrets or PII
- Rolling log files under server/Logs/log-.txt

## Architecture Decisions
- Repository pattern to encapsulate all data access
- Services handle all business logic and DTO mapping
- AutoMapper profiles located in server/Mappings/
- Dependency injection for all services registered in Program.cs

## Warnings
- Do not modify JWT hook without full testing — high risk
- Do not delete log files — prefer rotating old entries
- Always run dotnet test before touching core logic
- Confirm DefaultConnection before running migrations