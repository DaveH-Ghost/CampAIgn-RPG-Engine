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
3. Tag the release in git: `git tag v0.7.0 && git push origin v0.7.0`

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
uv pip install dist\realm_fabric-0.7.0-py3-none-any.whl
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
uv pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ realm-fabric==0.7.0
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
2. Update `docs/changelog/v0.x.x-changelog.md`
3. `uv build` → `uv publish`
4. Git tag `v0.x.x`

Do **not** re-upload the same version to PyPI — versions are immutable.

---

## What ships in the wheel

- `realm_fabric` (public API)
- `src` (engine + `realm` CLI entry point)
- `profiles/` (default game profiles)

**Not** in the wheel: `examples/` (realm-studio, minimal-server), `docs/`, `tests/`, `.env`, or other local dev files.
