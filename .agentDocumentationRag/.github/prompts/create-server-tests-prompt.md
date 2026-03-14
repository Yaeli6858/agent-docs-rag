Prompt: Generate C# xUnit Tests for Server-Side Code

Goal
- Produce maintainable C# test files that match the style and patterns already used in this project (xUnit `[Fact]`, Moq for mocking, FluentAssertions for assertions, and Arrange/Act/Assert structure).

Instructions for the LLM
- Input: caller will provide: the target C# file path (service, controller, or repository), file contents, and optional context (dependencies to mock, database context usage).
- Output: a single reply containing either:
  - a unified diff (patch) that adds the new test file(s) in the `SERVER.Tests` project, or
  - the exact file path(s) followed by the full test file content(s).

Requirements (match project patterns)
- Use xUnit test syntax with `[Fact]` attributes for individual test methods.
- Follow Arrange/Act/Assert (AAA) pattern with clear section comments.
- Use Moq (`Mock<T>`) to mock dependencies (repositories, services, ILogger, IMapper).
- Use FluentAssertions for all assertions (`.Should().Be()`, `.Should().NotBeNull()`, `.Should().ThrowAsync<TException>()`).
- Name test files `<ClassName>Tests.cs` and place them in the appropriate subfolder under `SERVER.Tests` (e.g., `Services/`, `Controllers/`).
- Test class should have:
  - Private readonly mock fields for all dependencies
  - Constructor that initializes mocks and creates the system under test (SUT)
  - Multiple `[Fact]` test methods covering normal flows, edge cases, and exceptions
- For async methods: use `async Task` and `await` in tests; use `.Should().ThrowAsync<TException>()` for exception tests.
- For controller tests: mock dependencies and assert return types (`ActionResult<T>`, `OkObjectResult`, `BadRequestResult`, etc.).
- Mock setup pattern: `_mockRepo.Setup(r => r.MethodAsync(param)).ReturnsAsync(value);`
- Keep tests focused: one logical assertion per test method when possible.

Formatting and delivery
- Include all necessary using statements at the top (`Xunit`, `Moq`, `FluentAssertions`, `AutoMapper`, `Microsoft.Extensions.Logging`, project namespaces).
- Use meaningful test method names following pattern: `MethodName_WhenCondition_ExpectedBehavior`.
- Add comments only for Arrange/Act/Assert sections.
- At the top of your reply include a one-line summary: what files were added and the main test strategies used.

Project-specific details
- Target framework: .NET 9.0
- Test packages: xUnit 2.9.2, Moq 4.20.72, FluentAssertions 8.8.0
- Test project: `SERVER.Tests/SERVER.Tests.csproj`
- Implicit usings and nullable reference types are enabled

Run instructions (for developer)
- Run tests from the solution root: `dotnet test` or `dotnet test SERVER.Tests/SERVER.Tests.csproj`
- Run with coverage: `dotnet test --collect:"XPlat Code Coverage"`

Examples of developer prompts for this generator
- "Path: server/Services/Implementations/GiftService.cs; File: <paste file contents>"
- "Path: server/Controllers/AuthController.cs; File: <paste file contents>; Mock: AuthService, ILogger"

Behavioral notes for the LLM
- Inspect the provided file and identify all constructor dependencies that need mocking.
- For services using repositories: mock the repository interface methods.
- For services using AutoMapper: mock `IMapper.Map<TDestination>(source)`.
- For services using ILogger: mock `ILogger<TService>` (no need to verify log calls unless specified).
- If a dependency or behavior is ambiguous, generate the test using reasonable defaults; avoid asking unless critical information is missing.
- Avoid modifying source files; only create new test files.

Changelog message
- Provide a short suggested commit message such as: "test: add tests for <ClassName> — covers success, edge cases, and exceptions"

End