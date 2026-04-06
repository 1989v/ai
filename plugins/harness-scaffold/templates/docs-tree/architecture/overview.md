# Architecture Overview

## Tech Stack

<!-- List primary languages, frameworks, and infrastructure components. -->

| Category | Technology | Version |
|----------|-----------|---------|
| Language | {{language}} | {{version}} |
| Framework | {{framework}} | {{version}} |
| Database | {{database}} | {{version}} |
| Messaging | {{messaging}} | {{version}} |
| Cache | {{cache}} | {{version}} |
| Container | {{container_platform}} | {{version}} |


## Layer Structure

<!-- Describe the architectural layers and the dependency direction between them. -->

```
{{layer_diagram}}
```

### Layer Responsibilities

| Layer | Responsibility | Allowed Dependencies |
|-------|---------------|---------------------|
| {{layer_1}} | {{layer_1_responsibility}} | {{layer_1_deps}} |
| {{layer_2}} | {{layer_2_responsibility}} | {{layer_2_deps}} |
| {{layer_3}} | {{layer_3_responsibility}} | {{layer_3_deps}} |
| {{layer_4}} | {{layer_4_responsibility}} | {{layer_4_deps}} |


## Key Dependencies

<!-- List critical external libraries or internal shared modules and their purpose. -->

| Dependency | Purpose |
|-----------|---------|
| {{dependency_1}} | {{purpose_1}} |
| {{dependency_2}} | {{purpose_2}} |


## Communication Patterns

<!-- Describe how services or modules communicate with each other. -->

### Synchronous

<!-- e.g. REST over HTTP, gRPC -->

{{synchronous_communication}}

### Asynchronous

<!-- e.g. Kafka events, message queues -->

{{asynchronous_communication}}

### Event Catalog

<!-- List key events/topics with their producers and consumers. -->

| Event / Topic | Producer | Consumer |
|---------------|---------|---------|
| {{event_1}} | {{producer_1}} | {{consumer_1}} |
| {{event_2}} | {{producer_2}} | {{consumer_2}} |
