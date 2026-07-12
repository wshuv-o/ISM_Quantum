# CB-SAFE on Kaggle: EMNIST + Edge-IIoTset generalization runs

This bundle runs the CB-SAFE robustness evaluation on two additional datasets to
strengthen the paper's generalization claim, using Kaggle's free GPU:

- **EMNIST-balanced** (47 classes, handwritten) — a larger, harder label space
  than CIFAR-10 / FashionMNIST.
- **Edge-IIoTset** (tabular IoT/IIoT intrusion detection) — a different modality
  (network-traffic features + MLP), matching the paper's IoT-security motivation.

It is **pure PyTorch** — no liboqs / crypto build is needed. (Masking correctness
is exact arithmetic, already proven dataset-independently on CIFAR-10; these runs
reuse the plain cluster-mean path for the robustness sweep.)

---

## Step-by-step

1. **Upload this zip as a Kaggle Dataset**
   Kaggle → *Datasets* → *New Dataset* → upload `cbsafe_kaggle.zip` → name it
   (e.g. `cbsafe-code`) → *Create*. Kaggle extracts it automatically.

2. **Add the Edge-IIoTset dataset** (for the tabular runs)
   In your notebook: *Add Data* → search **"Edge-IIoTset"** → add the dataset that
   contains `DNN-EdgeIIoT-dataset.csv` (title is usually
   *"Edge-IIoTset Cyber Security Dataset of IoT & IIoT"*).
   *(If you only want the EMNIST runs, you can skip this — the runner will detect
   the CSV is missing and just do EMNIST.)*

3. *(Optional, only if EMNIST auto-download fails)* **Add an EMNIST CSV dataset**
   Search *Add Data* for **"emnist"** and add e.g. `crawford/emnist` (has
   `emnist-balanced-train.csv` / `emnist-balanced-test.csv`). The runner tries
   torchvision first and falls back to this CSV automatically.

4. **Turn on GPU + Internet**
   Notebook sidebar → *Settings* → Accelerator = **GPU** (P100 or T4), Internet =
   **On**.

5. **Run one cell:**
   ```python
   import glob, subprocess, sys
   run = glob.glob('/kaggle/input/**/kaggle_run.py', recursive=True)[0]
   subprocess.run([sys.executable, run, '--out', '/kaggle/working/results'], check=True)
   ```
   This trains the full grid (2 attacks × 3 malicious fractions × 5 rules × 3
   seeds per dataset, plus baselines). Progress prints per run.

6. **Download the results**
   When it finishes (`KAGGLE RUN COMPLETE`), the CSVs are under
   `/kaggle/working/results/edgeiiot/` and `/kaggle/working/results/emnist/`.
   Zip and download:
   ```python
   import shutil; shutil.make_archive('/kaggle/working/cbsafe_results', 'zip',
                                       '/kaggle/working/results')
   ```
   Then download `cbsafe_results.zip` from the notebook's *Output* panel and send
   it back — the CSVs drop straight into the paper's analysis scripts.

---

## Notes

- **Resumable.** Every run writes one CSV and existing CSVs are skipped, so if a
  Kaggle session times out (12 h limit), just re-run the cell to continue.
- **Runtime.** Edge-IIoTset is fast (tabular, seconds/round). EMNIST is heavier;
  the full 3-seed grid may take a few hours. To do a quick first pass, limit it:
  ```python
  subprocess.run([sys.executable, run, '--out', '/kaggle/working/results',
                  '--datasets', 'edgeiiot', '--seeds', '0'], check=True)
  ```
- **Options:** `--datasets edgeiiot emnist`, `--seeds 0 1 2`, `--rounds 25`,
  `--n-clients 30`, `--cluster-size 3`.
- **Backdoor** runs on EMNIST only (it uses an image trigger); Edge-IIoTset runs
  sign-flip and label-flip.
