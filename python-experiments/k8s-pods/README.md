# list-k8s-pods 🐳

Tiny, beginner-friendly script to show the current Kubernetes context and list pods.

## Prerequisites ✅
- Python 3.8+ (macOS system Python may be managed; recommended to use a virtual environment)
- `kubectl` configured (so the kubeconfig has contexts and credentials)

## Install (recommended) 🛠️
Create and activate a virtual environment, then install the dependency:

```bash
python -m venv .venv
source .venv/bin/activate    # on macOS / Linux
.venv\Scripts\activate     # on Windows (PowerShell / cmd)
python -m pip install -U pip setuptools
python -m pip install -r requirements.txt
```

If you don't want a venv, you can also install the package globally or with `pipx`:

```bash
python -m pip install kubernetes    # or: pipx install kubernetes
```

## Usage 💡
Run the script from the project directory (inside the venv if you used one).

You can use `make` from the repository root for convenience:

```bash
# create venv and install deps (first time)
make install

# run the script (pass extra args with ARGS="--raw")
make run

# run across all namespaces
make run-all

# or run directly with the venv python
.venv/bin/python k8s-pods/list-k8s-pods.py -A
```

If you don't have make, use the direct python commands shown previously.

## What it prints
- A simple table with columns: namespace, pod name, ready containers, status, restart count, and node IP/name.

## Troubleshooting ⚠️
- If you see `ModuleNotFoundError: No module named 'kubernetes'`: activate your venv and run `pip install -r requirements.txt`.
- On macOS, if `pip install` fails due to an externally-managed environment, prefer creating a venv as shown above.

---