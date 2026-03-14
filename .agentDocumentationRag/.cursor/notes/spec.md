# Project Spec — Chinese Auction System

## Overview
Online raffle (Chinese auction) management system.
Roles: Admin, Donor, User.

## Frontend
- Framework: Angular
- Location: `client/`
- Dev server: `ng serve` at http://localhost:4200
- UI Library: PrimeNG

## Backend
- Framework: ASP.NET Core Web API
- Location: `server/`
- Target: .NET 8.0
- Database: SQL Server with Entity Framework Core
- Auth: JWT
- Logging: Serilog (writes to console and `server/Logs/log-.txt`)
- Mapping: AutoMapper
- API Docs: Swagger (available at `/swagger` in Development)

## Architecture
- Controllers → Services → Repositories → Database
- DTOs location: `server/DTOs/`
- Services location: `server/Services/`
- Repositories location: `server/Repositories/`
- Migrations location: `server/Migrations/`

## Testing
- Test project: `SERVER.Tests/`
- Use InMemory provider for repository tests
- Mock services for controller unit tests