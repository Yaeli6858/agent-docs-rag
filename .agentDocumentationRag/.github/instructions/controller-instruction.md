# Controllers — quick guidance

Purpose
- Controllers expose HTTP endpoints and should remain thin. They should validate input, call services, and return appropriate HTTP responses.

Where to look
- `server/Controllers/` — controller classes (AuthController, UserController, GiftController, etc.).

Guidelines
- Keep controllers thin: delegate business logic to services.
- Use attribute routing (`[Route("api/[controller]")]`) and action attributes (`[HttpGet]`, `[HttpPost]`, etc.).
- Use model binding and DTOs (`server/DTOs/`) for request/response shapes.
- Apply authorization using `[Authorize]` and role-based attributes where needed.
- For validation, use model validation attributes and return `BadRequest(ModelState)` when invalid.

Testing
- Add integration tests for controllers in `SERVER.Tests` when possible; for unit tests mock services.

Signature conventions
- Preferred signature example for actions that return data:

```csharp
public async Task<ActionResult<IEnumerable<CartItemResponseDto>>> GetCart()
```

- Guidance:
	- Use `Task<ActionResult<T>>` when your endpoint returns typed data and you want to leverage automatic content negotiation and helpful 200/404/400 responses.
	- Use `Task<IActionResult>` for endpoints that return different result shapes or status codes where no single DTO type represents the response.
	- Keep actions async and return Tasks for scalability.
	- Add a one-line header comment above the action indicating the return type (see earlier guideline).

	Security: trusted identity from token
	- For safe endpoints, do NOT accept user id or role from client input. Extract identity claims from the authenticated user (e.g., `User.FindFirst(ClaimTypes.NameIdentifier)` or role claims) and pass those values to the service.

	Example:

	```csharp
	var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
	if (userIdClaim == null) return Unauthorized();
	var userId = int.Parse(userIdClaim);
	var result = await _service.GetCartAsync(userId);
	```

	This prevents privilege escalation or tampering via client-supplied IDs.

