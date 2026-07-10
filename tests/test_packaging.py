"""Project packaging and pyproject.toml metadata."""

import importlib
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"


def _load_pyproject() -> dict:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))


def test_pyproject_version_is_semver():
    version = _load_pyproject()["project"]["version"]
    assert version == "1.0.0"
    assert re.fullmatch(r"\d+\.\d+\.\d+", version), version


def test_pyproject_has_no_console_scripts():
    data = _load_pyproject()
    assert "scripts" not in data["project"]
    assert data["tool"]["uv"]["package"] is True
    assert "hatchling" in data["build-system"]["requires"]


def test_hatch_builds_single_realm_fabric_package():
    data = _load_pyproject()
    hatch = data["tool"]["hatch"]["build"]
    assert hatch["packages"] == ["realm_fabric"]
    wheel = hatch["targets"]["wheel"]
    assert wheel["force-include"]["profiles"] == "profiles"


def test_built_wheel_contains_engine_code(tmp_path):
    import subprocess
    import zipfile

    dist = ROOT / "dist"
    wheels = sorted(dist.glob("realm_fabric-*.whl"))
    if not wheels:
        subprocess.run(["uv", "build"], cwd=ROOT, check=True)
        wheels = sorted(dist.glob("realm_fabric-*.whl"))
    assert wheels, "expected a built wheel in dist/"
    with zipfile.ZipFile(wheels[-1]) as zf:
        names = zf.namelist()
    assert any(n.startswith("realm_fabric/") and n.endswith(".py") for n in names)
    assert not any(n.startswith("src/") for n in names)
    assert not any(".env" in n for n in names)


def test_realm_fabric_public_imports():
    expected_version = _load_pyproject()["project"]["version"]
    rf = importlib.import_module("realm_fabric")
    assert rf.__version__ == expected_version
    assert rf.Session is not None
    assert rf.GameProfile is not None
    assert rf.PromptContext is not None
    assert rf.AgentCompoundTurn is not None
    assert rf.register_interaction_handler is not None
    assert rf.list_registered_handlers is not None
    assert rf.default_compound_profile is not None
    assert rf.build_area_snapshot is not None
    assert rf.build_session_snapshot is not None
    assert rf.DEFAULT_AREA_ID == "room"
    assert "Session" in rf.__all__
    assert rf.WorldMutationResult is not None
    assert rf.ObjectAction is not None
    assert "WorldMutationResult" in rf.__all__
    assert not hasattr(rf.Session, "run_command")


def test_pyproject_pypi_metadata():
    data = _load_pyproject()["project"]
    assert data["license"] == "MIT"
    assert data["authors"][0]["name"] == "DaveH-Ghost"
    assert data["authors"][0]["email"] == "davidhall.a27@gmail.com"
    assert "Homepage" in data["urls"]
    assert "Realm-Fabric" in data["urls"]["Repository"]
    classifiers = data["classifiers"]
    assert any("MIT License" in c for c in classifiers)


def test_license_file_exists():
    license_path = ROOT / "LICENSE"
    assert license_path.is_file()
    text = license_path.read_text(encoding="utf-8")
    assert "MIT License" in text
    assert "DaveH-Ghost" in text


def test_load_profile_builtin():
    from realm_fabric import load_profile

    profile = load_profile("default_compound")
    assert profile.profile_id == "default_compound"
    assert profile.schema_id == "AgentCompoundTurn"


def test_realm_fabric_modules_have_future_annotations():
    """Regression: PyPI installs on Python 3.12 need deferred annotation evaluation."""
    future = "from __future__ import annotations"
    pkg_root = ROOT / "realm_fabric"
    missing = [
        path.relative_to(ROOT).as_posix()
        for path in sorted(pkg_root.rglob("*.py"))
        if not any(line.strip() == future for line in path.read_text(encoding="utf-8").splitlines())
    ]
    assert not missing, f"missing {future!r}: {missing}"


def test_realm_fabric_imports_from_built_wheel(tmp_path):
    """Smoke-test the wheel the way PyPI users install it."""
    import subprocess
    import sys

    expected_version = _load_pyproject()["project"]["version"]
    subprocess.run(["uv", "build"], cwd=ROOT, check=True)
    wheels = sorted((ROOT / "dist").glob(f"realm_fabric-{expected_version}-*.whl"))
    assert wheels, f"expected wheel for {expected_version}"
    wheel = wheels[-1]

    venv_dir = tmp_path / "venv"
    subprocess.run(["uv", "venv", str(venv_dir)], cwd=ROOT, check=True)
    if sys.platform == "win32":
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:
        venv_python = venv_dir / "bin" / "python"
    subprocess.run(
        ["uv", "pip", "install", "--python", str(venv_python), str(wheel)],
        cwd=ROOT,
        check=True,
    )
    import_result = subprocess.run(
        [
            str(venv_python),
            "-c",
            "from realm_fabric import Session, __version__; "
            "assert Session is not None; print(__version__)",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert import_result.returncode == 0, import_result.stderr
    assert import_result.stdout.strip() == expected_version
