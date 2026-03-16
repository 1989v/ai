# {{project_name}} AI Working Agreement

## 1. Project Intent

<!-- Describe what this project builds, its business purpose, and key non-functional requirements. -->

{{project_intent}}


## 2. Architecture Principles

<!-- State the architectural style (e.g. Clean Architecture, Hexagonal, Layered) and the core rules that must not be violated. -->

{{architecture_principles}}


## 3. Module & Build Rules

<!-- Describe module layout, build tooling conventions, and any module-level restrictions. -->

{{module_and_build_rules}}

### Module Naming Convention

<!-- Provide a table or list of modules, their filesystem paths, and their roles. -->

| Module | Path | Role |
|--------|------|------|
| {{module_name}} | {{module_path}} | {{module_role}} |


## 4. Package Naming Convention

<!-- Define the base package and layer-by-layer package structure. -->

Base package: `{{base_package}}`

```
{{base_package}}/
├── {{layer_1}}/   # {{layer_1_description}}
├── {{layer_2}}/   # {{layer_2_description}}
├── {{layer_3}}/   # {{layer_3_description}}
└── {{layer_4}}/   # {{layer_4_description}}
```

- {{package_rule_1}}
- {{package_rule_2}}


## 5. Test Rules

<!-- Specify test framework, test double library, coverage expectations, and file naming conventions. -->

- Test framework: **{{test_framework}}**
- Test doubles: **{{test_double_library}}**
- Test file location: `src/test/{{lang}}/{{package}}/...`
- Test file naming: implementation name + `Test` suffix (e.g. `{{example_test_file}}`)

{{additional_test_rules}}


## 6. API Response Format

<!-- Define the standard HTTP response envelope used across all endpoints. -->

All HTTP responses are wrapped with `{{response_wrapper}}`.

**Success response:**
```json
{
  "success": true,
  "data": { "..." },
  "error": null
}
```

**Error response:**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "{{error_code_example}}",
    "message": "{{error_message_example}}"
  }
}
```

- {{api_response_rule_1}}
- {{api_response_rule_2}}
