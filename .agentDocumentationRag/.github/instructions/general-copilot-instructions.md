## Repository quickstart for coding agents

This repo is a full-stack "Chinese Auction / Raffle Management System" with an Angular frontend and ASP.NET Core backend.

Keep this file short and actionable so an agent seeing the repo for the first time can work efficiently.

Summary
- Purpose: online raffle (Chinese auction) management with roles for Admin, Donor and Users.
- Frontend: Angular app in `client/` (dev server: `ng serve` at http://localhost:4200).
- Backend: ASP.NET Core Web API in `server/` (TargetFramework: net8.0). Uses Entity Framework Core (SQL Server), JWT auth, Serilog, AutoMapper.

Tech stack
- Frontend: Angular (see `client/package.json`), TypeScript, SCSS.
  - UI / design libraries: this project includes PrimeNG (`primeng`, `primeicons`, `@primeng/themes`, `@primeuix/themes`). Check `client/angular.json` and `client/src/styles.scss` for theme and global style imports. When adding components, ensure corresponding UI module imports are added to the Angular module and any required CSS/theme files are included.
- Backend: .NET 8 (C#), ASP.NET Core Web API, EF Core with SQL Server provider, Serilog, Swashbuckle (Swagger).
- Tests: `SERVER.Tests/` contains server-side test project.

Project structure (high level)
- `/client` - Angular project. Typical Angular CLI layout: `src/`, `angular.json`, `package.json`.
- `/server` - ASP.NET Core Web API. Key files: `Program.cs`, `server.csproj`, `Controllers/`, `Data/`, `DTOs/`, `Services/`, `Repositories/`, `Mappings/`, `Migrations/`, `appsettings.json`.
- root `finalProject.sln` includes solution definitions.

Common tasks and commands
- Start frontend dev server: from `client/` run `npm install` once, then `npm run start` or `ng serve`.
- Build/Run backend locally: from `server/` use `dotnet build` then `dotnet run` (or launch via the solution in an IDE). The app reads connection string `DefaultConnection` from `appsettings.json`.
- Run server tests: `dotnet test SERVER.Tests/SERVER.Tests.csproj` from repo root.

Important notes and guidelines for an agent
- Do not run shell commands that assume a UNIX environment; this repo is worked on in Windows. Use powershell-compatible commands when instructing or running locally.
- Dotnet SDK: project targets .NET 8.0. Ensure the environment has .NET 8 SDK installed before attempting builds/runs.
- SQL Server: EF Core is configured for SQL Server. If you run migrations or start the server, ensure a reachable SQL Server instance and `DefaultConnection` in `appsettings.json` (or override via environment variables). When in doubt, stub DB interactions in unit tests or use the InMemory provider for feature work.
- Secrets and JWT: app uses user secrets (`UserSecretsId` in csproj). Avoid attempting to read secrets from external stores in an ephemeral environment; prefer mocking for local dev.
- Logs: Serilog writes to console and `server/Logs/log-.txt` by rolling day files. Avoid deleting logs blindly; prefer rotating or trimming old entries if needed.

Coding conventions & guidelines
- C# / .NET
  - Follow existing naming conventions (PascalCase for public types/methods, camelCase for private fields with _ prefix where present).
  - Keep controllers thin: business logic belongs in Services/Repositories.
  - Use async/await for I/O-bound operations and return Task-based signatures.
  - Use dependency injection; register new services in `Program.cs`.
  - Add unit tests for new services/controllers in `SERVER.Tests` when possible.

- Angular
  - Use Angular CLI for generators. Preserve existing TypeScript/SCSS styles and module structure.

Search & quick markers
- Look for migrations in `server/Migrations/` when schema changes are needed.
- Common TODO/HACK markers: none prominent in codebase but search for `TODO`, `HACK`, `FIXME`, `XXX` before touching ambiguous areas.

Developer resources in the repo
- `README.md` (root) and `client/README.md` contain basic run/build notes.
- `server/server.csproj`, `server/Program.cs` show package references and runtime wiring.
- Swagger is enabled in Development; use it to explore APIs once server runs (usually at `/swagger`).

Safety checklist before changes
1. Run unit tests (if modifying core logic): `dotnet test`.
2. Build server: `dotnet build server/server.csproj`.
3. If migration needed, add EF Core migration with `dotnet ef migrations add Name` using the Tools package; run only after confirming connection string and environment.

Minimal troubleshooting tips
- If `dotnet build` fails with package or target errors, confirm .NET SDK version (`dotnet --info`).
- If DB connection fails, use InMemory provider in tests or set `DefaultConnection` to a local SQL Server / LocalDB instance.
- If Angular build fails, remove `node_modules` and reinstall `npm ci`.

If you will implement a change
- Read `Program.cs` to understand registered services and middleware before adding controllers/services.
- Add tests for any non-trivial business logic to `SERVER.Tests` and run them.

Contact points
- No direct maintainer contacts in repo. Use PR description with context when opening changes.

Last notes
- Keep the instructions concise. If you need more detail while working on a specific change, update this file with notes discovered during development.

 
