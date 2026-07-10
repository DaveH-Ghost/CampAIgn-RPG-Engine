# Releasing to PyPI (maintainers)

**Repo maintainer notes** — not for app authors or realm-studio users. End users install with `pip install realm-fabric` or `uv add realm-fabric` once a release is on PyPI.

Package name: **`realm-fabric`**. License: **MIT** (`LICENSE`, `pyproject.toml`).

---

## Metadata

| Field | Location |
|-------|----------|
| License | `LICENSE`, `license = "MIT"` in `pyproject.toml` |
| Author | `authors` in `pyproject.toml` |
| Docs / repo URLs | `[project.urls]` in `pyproject.toml` |

---

## Prerequisites

1. [PyPI account](https://pypi.org/account/register/) (and [TestPyPI](https://test.pypi.org/) for dry runs)
2. API token: PyPI → Account settings → API tokens (scope: whole account or project `realm-fabric`)
3. Tag the release in git: `git tag v1.0.0 && git push origin v1.0.0`

---

## Build locally

```powershell
cd path\to\Realm-Fabric
uv sync
uv build
```

Artifacts land in `dist/` (`.whl` and `.tar.gz`).

### Verify install from wheel

```powershell
uv venv .venv-pypi-test
.\.venv-pypi-test\Scripts\Activate.ps1
uv pip install dist\realm_fabric-1.0.0-py3-none-any.whl
python -c "from realm_fabric import Session, __version__; print(__version__)"
```

---

## Publish to TestPyPI (recommended first)

```powershell
$env:UV_PUBLISH_USERNAME = "__token__"
$env:UV_PUBLISH_PASSWORD = "pypi-..."   # TestPyPI token

uv publish --publish-url https://test.pypi.org/legacy/
```

Install from TestPyPI:

```powershell
uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ realm-fabric==1.0.0
```

(`--extra-index-url` pulls dependencies like pydantic from main PyPI.)

---

## Publish to PyPI

```powershell
$env:UV_PUBLISH_USERNAME = "__token__"
$env:UV_PUBLISH_PASSWORD = "pypi-..."   # PyPI token

uv publish
```

---

## Version bumps

1. Bump `version` in `pyproject.toml` (`realm_fabric.__version__` reads it automatically)
2. Add or update `docs/changelog/vX.Y.Z-changelog.md` and the [changelog index](changelog/README.md)
3. `uv build` → `uv publish`
4. Git tag `vX.Y.Z`

Do **not** re-upload the same version to PyPI — versions are immutable.

---

## What ships in the wheel

- `realm_fabric` (public API)
- `profiles/` (default game profiles)

**Not** in the wheel: `examples/`, `docs/`, `tests/`, `.env`, or other local dev files. No CLI entry point in 1.0+.
