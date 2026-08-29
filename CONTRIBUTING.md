# Contribuir a PlankAI

Desarrollo solitario con **GitFlow flexible** y **conventional commits**.

## Convenciones de commits

```
<type>(<scope>): <description>

Tipos: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
```

Ejemplos:
```
feat(blueprint): add DWG file parser
fix(cutting): correct waste calculation
docs: update installation guide
chore: configure Gentle AI ecosystem
```

## Ramas

| Rama | Propósito | Merge hacia |
|------|-----------|-------------|
| `main` | Producción | — |
| `develop` | Desarrollo | `main` |
| `feature/*` | Nuevas funcionalidades | `develop` |
| `release/*` | Preparar release | `develop` + `main` |
| `hotfix/*` | Corrección crítica | `main` + `develop` |

## Flujo típico

```bash
# Feature
git checkout develop
git checkout -b feature/mi-feature
# ... trabajar ...
git commit -m "feat(scope): descripción"
git push -u origin feature/mi-feature
# Crear PR → develop (opcional pero recomendado)

# Release
git checkout -b release/v1.0 develop
# ... preparar ...
git push -u origin release/v1.0
# Crear PR → develop + main

# Hotfix
git checkout -b hotfix/corregir-error main
# ... corregir ...
git push -u origin hotfix/corregir-error
# Crear PR → main + develop
```

## Reglas

- **Conventional commits** obligatorios
- **Push directo a `main`** permitido (solo dev)
- **PRs opcionales** pero recomendados para cambios importantes
- **Squash merge** preferido para mantener historial limpio

## Herramientas

- **Gentle AI** — Ecosistema configurado (Engram, SDD, Skills)
- **OpenCode** — Agente de IA para desarrollo
- **GGA** — Guardian Angel para hooks de código
