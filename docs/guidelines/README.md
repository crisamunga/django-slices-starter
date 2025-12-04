# Guidelines Hub

Welcome to the guidelines hub for this Django project. This folder collects practical conventions and patterns for consistent, maintainable code across slices.

Use this page as your starting point; each section links to a focused guideline with examples.

## Essentials
- `python-guidelines.md`: Core Python style, typing, error handling, logging, and module structure used across the repo.
- `models-guidelines.md`: Django models best practices, field choices, indexes, signals, and migrations.
- `slices-guidelines.md`: Principles for building modular “slices” (domain packages), boundaries, and integration patterns.

## APIs
- `rest-api-guidelines.md`: Building REST resources, serializers, pagination, errors, and versioning.
- `graphql-guidelines.md`: GraphQL schema design, types, mutations, loaders, and performance.

## Behavior & Access
- `permissions-guidelines.md`: Designing permission checks, reusability, and consistent enforcement.
- `validators-guidelines.md`: Input validation patterns, reusable validators, and error messaging.

## Services
- `services-guidelines.md`: Service layer architecture, orchestration, idempotency, and reliability.

## Testing

- `testing-guidelines.md`: Testing strategy, fixtures/factories, isolation, and coverage targets.

## How to Use
- Start with the Essentials, then read the API or Behavior sections relevant to your work.
- When adding a new feature:
	- Define boundaries in a slice per `slices-guidelines.md`.
	- Model data following `models-guidelines.md`.
	- Expose functionality via REST or GraphQL per their guidelines.
	- Enforce access in `permissions-guidelines.md` and validate inputs per `validators-guidelines.md`.
	- Implement orchestration in the services layer.
	- Write tests aligned with `testing-guidelines.md`.

## Contributing
- Keep examples minimal and realistic; prefer patterns over one-off solutions.
- Update the relevant guideline when introducing new conventions.
- Ensure changes remain consistent with the wider project style in `python-guidelines.md`.

## Quick Links
- [Python](python-guidelines.md)
- [Models](models-guidelines.md)
- [Slices](slices-guidelines.md)
- [REST](rest-api-guidelines.md)
- [GraphQL](graphql-guidelines.md)
- [Services](services-guidelines.md)
- [Permissions](permissions-guidelines.md)
- [Validators](validators-guidelines.md)
- [Testing](testing-guidelines.md)
