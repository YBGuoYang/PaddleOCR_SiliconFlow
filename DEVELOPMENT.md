# Development

## Recommended Python

Use Python 3.10 to 3.13 on Windows.

Python 3.14 is not recommended yet because key packages such as `Pillow` may not be available.

## First-Time Setup

From the project root:

```powershell
.\setup_env.bat --dev
```

This creates `.venv` and installs both runtime and development dependencies.

## Run

The official source entry is:

```powershell
.\run.bat
```

`run_hotkey.bat` is kept as a compatibility alias and launches the same tray + hotkey flow.

## Build

```powershell
.\build.bat
```

## Packaging

```powershell
.\package_source.bat
.\package_release.bat
.\package_all.bat
```

## Notes

- If your network to PyPI is unstable, configure a mirror before running `setup_env.bat`.
- Use `.venv\Scripts\python.exe` for local verification and tests.
- Do not commit `dist/`, `build/`, or release zip files.
- Release checklist: `docs/RELEASE.md`
