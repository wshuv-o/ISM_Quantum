# Setup & environment (Phase 1)

This records the exact, reproducible environment for the project. Phase 1 of the build plan
("Environment") is **complete**: liboqs exposes HQC and Kyber/ML-KEM and all KEMs pass an
encaps/decaps round-trip on this machine.

## Interpreter

We reuse an existing CUDA-enabled env rather than creating a new one (the D: drive has too little
free space for a second PyTorch install):

```
D:\EEG-TransNet\testenv\python.exe   # Python 3.12.3, torch 2.5.0 + CUDA 12.4, RTX 2060 (6 GB)
```

Packages added for this project: `flwr==1.32.0`, `cryptography==46.0.7`,
`liboqs-python==0.15.0`, `cmake`, `ninja`.

> Shared-env caveat: installing flwr downgraded `typer` to 0.20.1, which conflicts with
> `openneuro-py` used by the unrelated EEG-TransNet project in the same env.

## Required environment variables

| Variable | Value | Why |
|---|---|---|
| `OQS_INSTALL_PATH` | `C:\Users\Shuvo\_oqs` | so `import oqs` finds the locally-built liboqs (set automatically by `src/crypto/kem.py`) |
| `KMP_DUPLICATE_LIB_OK` | `TRUE` | avoids "OMP: Error #15" from the MKL/torch OpenMP clash on Windows; set **before** importing torch/numpy |

## liboqs (the HQC / Kyber core)

This machine has **no MSVC compiler**, so the `liboqs-python` auto-build fails. liboqs was built
from source with a portable clang toolchain (no admin):

- Toolchain: `llvm-mingw` at `C:\Users\Shuvo\llvm-mingw-20260616-ucrt-x86_64\` + pip `ninja`.
- Output: a self-contained `liboqs.dll` (only KERNEL32/ADVAPI32/UCRT deps) installed to
  `C:\Users\Shuvo\_oqs\bin\liboqs.dll`.
- **HQC is OFF by default in liboqs** and was enabled with `-DOQS_ENABLE_KEM_HQC=ON`.

Full rebuild commands:

```bash
LLVM="C:/Users/Shuvo/llvm-mingw-20260616-ucrt-x86_64/bin"
export PATH="$LLVM:/d/EEG-TransNet/testenv/Scripts:$PATH"
CMAKE="/d/EEG-TransNet/testenv/Scripts/cmake.exe"
git clone --branch 0.15.0 --depth 1 https://github.com/open-quantum-safe/liboqs
"$CMAKE" -S liboqs -B liboqs/build -G Ninja \
  -DCMAKE_C_COMPILER="$LLVM/clang.exe" -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_SHARED_LIBS=ON -DOQS_BUILD_ONLY_LIB=ON -DOQS_USE_OPENSSL=OFF \
  -DOQS_ENABLE_KEM_HQC=ON -DCMAKE_INSTALL_PREFIX="C:/Users/Shuvo/_oqs"
"$CMAKE" --build liboqs/build --parallel 4 && "$CMAKE" --install liboqs/build
```

> On Linux (Colab/Kaggle) none of this is needed: `pip install liboqs-python` auto-builds liboqs
> with the preinstalled gcc. Enabling HQC there still requires building liboqs with
> `OQS_ENABLE_KEM_HQC=ON` (set `PYOQS_VERSION`/build env or pre-build liboqs).

## HQC provenance (state this in the paper)

liboqs 0.15.0 ships the **PQClean "clean" HQC implementation, spec version 2023-04-30** — the
Round-4 submission NIST selected in March 2025 — IND-CCA2, constant-time claimed. It is disabled
by default pending the finalized standard. We use it as the representative HQC for cost
benchmarking; final standardized parameters may differ slightly.

## Verify

```bash
python scripts/check_env.py     # round-trips all KEMs, writes results/crypto_kem_bench.csv
```
