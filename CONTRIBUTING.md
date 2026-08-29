# Contribuir a PlankAI

Seguimos el flujo de trabajo **GitFlow**. Todas las ramas principales (`main` y `develop`) están protegidas: no se permite el push directo, solo se integran cambios vía Pull Request.

## Ramas principales

| Rama | Propósito |
|------|-----------|
| `main` | Código en producción. Solo se mergea desde `release/*` o `hotfix/*`. |
| `develop` | Código en desarrollo. Solo se mergea desde `feature/*`, `bugfix/*` o `hotfix/*`. |

## Ramas de apoyo

| Tipo | Desde | Hacia | Ejemplo |
|------|-------|-------|---------|
| `feature/*` | `develop` | `develop` | `feature/formulario-contacto` |
| `release/*` | `develop` | `develop` + `main` | `release/v1.0` |
| `bugfix/*` | `release` | `release` | `bugfix/soporte-para-ios` |
| `hotfix/*` | `main` | `main` + `develop` | `hotfix/error-en-certificado-ssl` |

## Flujo

```
main        ← solo merge de release/* y hotfix/*
  ↑
develop     ← solo merge de feature/*, bugfix/*, hotfix/*
  ↑
feature/*   ← desde develop
release/*   ← desde develop
bugfix/*    ← desde release
hotfix/*    ← desde main
```

## Cómo crear una rama de feature

```bash
git checkout develop
git pull
git checkout -b feature/mi-nueva-funcionalidad

# ... trabajar ...

git add .
git commit -m "feat: mi nueva funcionalidad"
git push -u origin feature/mi-nueva-funcionalidad
```

Luego crear un Pull Request hacia `develop` en GitHub.

## Cómo crear un release

```bash
git checkout develop
git pull
git checkout -b release/v1.0

# ... preparar release (bump version, changelog, etc.) ...

git add .
git commit -m "chore: prepare release v1.0"
git push -u origin release/v1.0
```

Luego crear dos Pull Requests:
1. `release/v1.0` → `develop`
2. `release/v1.0` → `main`

## Cómo crear un hotfix

```bash
git checkout main
git pull
git checkout -b hotfix/corregir-error-critico

# ... corregir el bug ...

git add .
git commit -m "fix: corregir error critico"
git push -u origin hotfix/corregir-error-critico
```

Luego crear dos Pull Requests:
1. `hotfix/corregir-error-critico` → `main`
2. `hotfix/corregir-error-critico` → `develop`

## Reglas

- **No hacer push directo** a `main` ni `develop`.
- **Siempre crear un PR** para integrar cambios.
- **Usar el prefijo correcto** en los nombres de rama: `feature/`, `release/`, `bugfix/`, `hotfix/`.
- **Squash merge** es el método de merge preferido para mantener el historial limpio.
- Los PRs requieren **al menos 1 approval** antes de ser mergeados.
