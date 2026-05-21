# Configuring `uv` with Non-Standard Virtual Environment Locations

A guide to how `uv` handles virtual environments, how to override its defaults, and a specific reference for a sibling-folder venv layout on Windows CMD.

---

## Part 1: General Reference — How `uv` Handles Virtual Environments

This section is for anyone trying to understand `uv`'s environment-discovery behavior and the levers available for non-standard setups.

### The Default Behavior

`uv` is opinionated: by default it assumes each project owns its own virtual environment at `.venv/` in the project root. When you run a project command (`uv sync`, `uv add`, `uv run`, `uv lock`, etc.) it will:

1. Look for `.venv/` in the current directory (or the nearest parent containing a `pyproject.toml`)
2. If it doesn't find one, **create it automatically**
3. Install/sync packages into that `.venv/`

This is great for the common case but actively fights any workflow where venvs live somewhere else.

### What `uv` Does With `VIRTUAL_ENV`

This is the part that surprises most people coming from `pip`/`venv` workflows:

> **`uv` does NOT respect `VIRTUAL_ENV` for project commands by default.**

If you `activate` a venv and then run `uv sync`, `uv` will:

- Print a warning: `VIRTUAL_ENV=... does not match the project environment path '.venv' and will be ignored`
- Create or use `.venv/` in the project root anyway
- Install everything into `.venv/`, not your activated environment

This is intentional — `uv` treats the project environment as something *it* manages, not something the user activates externally.

The pip-compatibility subcommands (`uv pip install`, `uv pip sync`) DO respect `VIRTUAL_ENV` — but the modern project commands do not.

### The Three Escape Hatches

`uv` provides three ways to opt out of the default behavior:

#### 1. The `--active` flag

Pass `--active` to any project command and `uv` will respect the activated `VIRTUAL_ENV`:

```bash
source /path/to/my-venv/bin/activate
uv sync --active
uv add --active requests
```

**Pros:** Explicit, per-command opt-in.
**Cons:** You must remember it every single time. Easy to forget and accidentally create a stray `.venv/`.

#### 2. `UV_PROJECT_ENVIRONMENT` environment variable

This tells `uv` where the project's environment *actually lives*. When set, `uv` treats that path as the canonical project environment — no `--active` needed, no warning emitted.

```bash
export UV_PROJECT_ENVIRONMENT="/path/to/my-venv"
uv sync   # uses the specified path
```

**Pros:** Set once, works for all project commands. Eliminates the warning entirely. `uv` "takes ownership" of the external path cleanly.
**Cons:** The path is project-specific, so you can't just set it globally — you need a per-project mechanism (a `.envrc`, a shell function, an activation wrapper, etc.).

#### 3. `UV_ACTIVE` (does not yet exist)

There's an open feature request ([uv#11273](https://github.com/astral-sh/uv/issues/11273)) to add a `UV_ACTIVE=1` environment variable as the env-var equivalent of `--active`. As of this writing it's not merged.

Setting `UV_ACTIVE=1` does *nothing* — `uv` silently ignores it. Don't be fooled.

### Common Patterns for Non-Standard Layouts

#### Sibling-folder venvs (e.g., `../virtualenvs/<project>`)

This layout keeps source code and venvs separate, often used to keep IDE indexers happy or to share venvs across related projects. Use `UV_PROJECT_ENVIRONMENT` set by a wrapper script.

#### Centrally managed venvs (e.g., `~/.virtualenvs/<project>` or `pyenv-virtualenv`)

Same pattern — `UV_PROJECT_ENVIRONMENT` pointed at the central location, often combined with `direnv` or shell hooks for auto-activation.

#### Conda/mamba environments

Set `UV_PROJECT_ENVIRONMENT=$CONDA_PREFIX` after activating the conda env. `uv` will then manage Python packages inside the conda env without trying to create its own `.venv/`.

### Why `--active` Alone Isn't Always Enough

Even with `--active`, some edge cases bite:

- If a local `.venv/` already exists from a previous run, `uv` may still prefer it in some commands.
- The warning still prints on every command unless you also pass `--no-active` (which doesn't make sense alongside `--active`).
- Forgetting the flag once creates `.venv/` and you have to clean up.

`UV_PROJECT_ENVIRONMENT` avoids all of this because it changes what `uv` considers the canonical environment, rather than asking it to tolerate a non-canonical one.

### Cleanup of Stray `.venv/` Directories

If `uv` has previously created an unwanted `.venv/`, delete it before relying on `UV_PROJECT_ENVIRONMENT`:

```bash
# macOS/Linux
rm -rf .venv

# Windows CMD
rmdir /s /q .venv
```

Otherwise the local `.venv/` may still win the environment-discovery race in some edge cases.

### Platform-Specific Setup Patterns

| Shell / OS                   | Recommended approach                                              |
| ---------------------------- | ----------------------------------------------------------------- |
| bash/zsh + direnv            | `.envrc` exporting `UV_PROJECT_ENVIRONMENT` per project          |
| bash/zsh, no direnv          | `PROMPT_COMMAND` mirroring `VIRTUAL_ENV` → `UV_PROJECT_ENVIRONMENT` |
| PowerShell                   | `prompt` function in `$PROFILE` mirroring the same                |
| Windows CMD                  | A wrapper `.bat` on `PATH` that sets the var and activates       |
| Conda/mamba                  | Shell function that sets `UV_PROJECT_ENVIRONMENT=$CONDA_PREFIX`  |

---

## Part 2: Personal Reference — Andrew's Setup

This section documents the specific configuration on this Windows CMD machine. Layout convention: project source lives in `C:\Users\andrew.festa\Documents\projects\<name>\`, and its venv lives at `C:\Users\andrew.festa\Documents\projects\virtualenvs\<name>\` (sibling to the project folder).

### The Goal

Run any `uv` project command (`uv sync`, `uv add`, etc.) from a project directory and have it automatically target the sibling-folder venv, without `--active` and without creating a stray `.venv/` in the project root.

### The Mechanism

A single batch file, `uv_activate.bat`, placed somewhere on `PATH`. When run from a project root, it:

1. Derives the project name from the current directory
2. Computes the venv path as `..\virtualenvs\<project_name>`
3. Sets `UV_PROJECT_ENVIRONMENT` to that path
4. Calls the venv's `activate.bat` to also activate it normally

This means `uv` *and* normal Python both work correctly with no per-command flags.

### The Script

**Location:** `C:\Users\andrew.festa\bin\uv_activate.bat`
(Or wherever you placed it — must be on `PATH`.)

```bat
@echo off
if "%~1"=="" (
    for %%I in ("%CD%") do set "UV_PROJECT_ENVIRONMENT=%CD%\..\virtualenvs\%%~nxI"
) else (
    set "UV_PROJECT_ENVIRONMENT=%~f1"
)
call "%UV_PROJECT_ENVIRONMENT%\Scripts\activate.bat"
```

**Behavior:**
- `uv_activate` (no arg) — auto-derives venv path from the current directory name
- `uv_activate <path>` — uses the explicit path you provide

### PATH Setup

`C:\Users\andrew.festa\bin` was added to the user PATH so `uv_activate` is callable from anywhere:

```cmd
setx PATH "%PATH%;C:\Users\andrew.festa\bin"
```

(Note: `setx` only affects future shells, not the current one. Open a fresh CMD after running it.)

### Registry State (AutoRun)

Earlier in setup, an AutoRun entry was added to `HKCU\Software\Microsoft\Command Processor\AutoRun` pointing at `uv_python_init.bat` for doskey macros. **This has been removed** because the `uv_activate.bat` approach handles everything without needing AutoRun macros.

If for any reason the AutoRun entry comes back or causes "is not recognized" errors at every CMD startup, remove it with:

```cmd
reg delete "HKCU\Software\Microsoft\Command Processor" /v AutoRun /f
```

Verify it's gone:

```cmd
reg query "HKCU\Software\Microsoft\Command Processor" /v AutoRun
```

Expected output: `ERROR: The system was unable to find the specified registry key or value.`

### Daily Workflow

From a fresh CMD window:

```cmd
cd Documents\projects\skill_evolution
uv_activate
uv sync
```

Expected behavior:
- Prompt gains the `(skill_evolution)` prefix (venv activated)
- `echo %UV_PROJECT_ENVIRONMENT%` shows the full sibling path
- `uv sync` reports "Resolved N packages" with **no** "Creating virtual environment at: .venv" line
- No warning about `VIRTUAL_ENV` mismatch

### Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `uv sync` creates `.venv/` in project root | `UV_PROJECT_ENVIRONMENT` wasn't set in this shell | Run `uv_activate` first; verify with `echo %UV_PROJECT_ENVIRONMENT%` |
| Warning: `VIRTUAL_ENV does not match the project environment path` | Activated venv, but `UV_PROJECT_ENVIRONMENT` wasn't set | Same fix — use `uv_activate` instead of raw `activate.bat` |
| `'uv_activate' is not recognized` | `C:\Users\andrew.festa\bin` not on PATH, or shell predates the `setx` | Open a fresh CMD window; verify with `where uv_activate` |
| `'C:\...\<name>.bat' is not recognized` on every CMD startup | Stale AutoRun registry entry pointing to a missing file | Run the `reg delete` command above |
| `echo %UV_PROJECT_ENVIRONMENT%` returns literal `%UV_PROJECT_ENVIRONMENT%` | Var not set in this shell | Run `uv_activate` |
| Stray `.venv/` from earlier mistakes | Existed before fix | `rmdir /s /q .venv` then `uv_activate` then `uv sync` |

### Notes on `setx` and PATH

`setx` is permanent but does not affect the current shell. If `uv_activate` is "not recognized" right after running `setx`, open a new CMD window. To verify the PATH change:

```cmd
echo %PATH%
where uv_activate
```

### Things That Did NOT Work (so I don't try them again)

1. **`UV_ACTIVE=1` as a system variable** — `uv` ignores it. The variable is not implemented as of mid-2026; only an open feature request exists.
2. **`doskey` macros via AutoRun** — Doskey is finicky with multi-step macros; the `$b` separator pipes commands (so `set` runs in a subshell and the variable evaporates). `$T` is the correct doskey escape for `&`, but real `.bat` scripts on PATH are simpler and more debuggable.
3. **Just activating the venv with `activate.bat`** — `uv` ignores `VIRTUAL_ENV` for project commands and recreates `.venv/`. The whole reason `uv_activate.bat` also sets `UV_PROJECT_ENVIRONMENT` is to bridge this gap.

### Future Migration Path

If/when `UV_ACTIVE` lands upstream (see [uv#11273](https://github.com/astral-sh/uv/issues/11273)), the setup can simplify to:

```cmd
setx UV_ACTIVE 1
```

…and then a plain `activate.bat` would be sufficient. Until then, the `uv_activate.bat` wrapper is the cleanest approach.
