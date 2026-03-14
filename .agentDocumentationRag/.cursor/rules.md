# Cursor Rules — Chinese Auction Project

## Environment
- Windows only — use PowerShell commands
- Frontend: Angular with TypeScript and SCSS
- Backend: ASP.NET Core .NET 8 with C#

## Code Style
- Controllers must stay thin — business logic belongs in Services
- Use async/await for all I/O-bound operations
- PascalCase for public methods, camelCase with _ prefix for private fields

## Security
- Never accept userId from client input — always extract from JWT Token
- Never store secrets in code — use User Secrets
- Do not modify JWT authentication without full testing

## UI
- UI library: PrimeNG only
- Ensure all modules import required PrimeNG components
- RTL required for all Hebrew content