# Services — quick guidance

Purpose
- Services contain business logic and orchestrate repositories, external integrations, and domain rules.

Where to look
- `server/Services/Implementations` — concrete service classes.
- `server/Services/Interfaces` — service contracts.

Guidelines
- Keep services unit-testable: inject repositories and external dependencies via constructor injection.
- Prefer small, single-responsibility services; if methods grow large, extract helper services.
- Use async/await for I/O-bound operations and return Task-based signatures.
- Handle exceptions at boundaries; let middleware (`server/Middlewares/ExceptionHandlingMiddleware.cs`) produce consistent error responses.
 - Responsibility: services are the place to map domain models/entities to DTOs for transport. Use AutoMapper profiles (`server/Mappings`) or manual mapping in services; do NOT map entities in repositories.

Testing
- Add unit tests to `SERVER.Tests/Services` using mocked repository interfaces.

Logging
- The project uses Serilog (configured in `Program.cs`). Serilog writes to console and to rolling files under `server/Logs/log-.txt` by default. Review `Program.cs` for the exact configuration and retained file count.
- Best practices:
  - Use structured logging: prefer `logger.LogInformation("Processed {GiftId} in {ElapsedMs}ms", id, elapsedMs)` over string concatenation.
  - Do not log secrets or PII. Mask or exclude sensitive fields before logging.
  - Inject `ILogger<T>` into services via DI and use it for scoped logs.
  - Use appropriate log levels (Debug/Information/Warning/Error/Critical) and include contextual properties when useful.

Example (constructor injection):

```csharp
public class GiftService : IGiftService
{
	private readonly ILogger<GiftService> _logger;
	public GiftService(ILogger<GiftService> logger /*, other deps */)
	{
		_logger = logger;
	}

	public async Task<GiftDto> GetByIdAsync(int id)
	{
		_logger.LogInformation("Getting gift {GiftId}", id);
		// ...
	}
}
```
