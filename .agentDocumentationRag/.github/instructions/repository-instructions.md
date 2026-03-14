# Repositories — quick guidance

Purpose
- Repositories are responsible for data access and encapsulate Entity Framework Core operations against the `AppDbContext`.

Where to look
- `server/Repositories/Implementations` — concrete EF-backed repositories.
- `server/Repositories/Interfaces` — repository interfaces.

Guidelines
- Keep repository methods focused on data access (queries, updates). Avoid business logic here.
- Use async EF Core APIs (`ToListAsync`, `FirstOrDefaultAsync`, etc.).
- Return domain models / EF entities from repositories. Repositories MUST NOT perform mapping to DTOs; mapping is the responsibility of the service layer. This keeps repositories focused on data access and simplifies testing.
- If performance requires returning a specific shape, return lightweight domain projections (value objects) from repository and map in service — avoid returning transport DTOs directly from repository.
- When adding migrations, run EF Core commands from `server/` and confirm `DefaultConnection` is set correctly.

Testing
- Use an EF InMemory provider for repository tests, or a test SQL instance for integration-style tests.
