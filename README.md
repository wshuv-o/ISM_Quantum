# A Code-Based Post-Quantum Framework for Secure Aggregation in Federated Learning

**Team:** Md Wahiduzzaman Suva (26-94088-2), Esm-e Moula Chowdhury Abha (26-94089-2)

This README is the project context for continuing the work in Claude Code. It captures the
finalized topic, the design decisions made during planning, the build plan, and the
constraints. Read it first before writing code.

---

## 1. One-line summary

Every existing post-quantum federated learning system is built on **lattice** cryptography.
If lattices are ever weakened, they all fall together. This project builds the **first
federated learning secure-aggregation framework whose post-quantum security comes from a
code-based scheme (HQC)** instead of lattices, and measures honestly what that diversity costs.

## 2. The contribution (what we are actually building)

- A secure-aggregation protocol for federated learning where the key establishment uses the
  **HQC key-encapsulation mechanism (KEM)** — the code-based scheme NIST selected in March 2025
  as a non-lattice alternative to Kyber — instead of a lattice KEM.
- A method to keep per-round communication practical despite HQC's **much larger ciphertexts**.
- An honest empirical comparison (communication, computation, accuracy, robustness) of the
  **code-based (HQC)** variant against a **lattice-based (Kyber)** baseline on public datasets.
- A reproducible, open implementation others can benchmark against.

## 3. Honest framing (do NOT overclaim — keep this discipline)

- The novelty is **cryptographic diversity** (being first to bring code-based crypto into FL),
  motivated by NIST's own reason for standardizing HQC. It is **not** a claim of beating
  lattices on speed or size — HQC is heavier, and we expect to show a diversity-vs-cost tradeoff.
- The reviewer's first question will be *"isn't this just swapping the primitive?"* The answer,
  and the reason it's a paper: HQC's size/structure make the swap **non-trivial** in the FL loop,
  so the real work is making code-based secure aggregation practical and characterizing the cost.
- If HQC turns out too heavy, the **quantified negative result** is itself a useful finding.
- The "first to use code-based crypto in FL" claim is *to the best of our knowledge from the
  literature scan* — keep checking as new papers appear; that's the claim reviewers will test.

## 4. Important technical note (architecture decision)

**HQC is a KEM, not a signature scheme.** It establishes shared secrets / encapsulates keys; it
cannot sign. There is **no standardized code-based signature scheme**. So:

- HQC's natural place is the **confidentiality / secure-aggregation key-establishment layer**:
  clients use HQC to establish pairwise shared secrets, derive masks, mask their model updates,
  and the server aggregates so masks cancel (the Bonawitz-style masking pattern, with the
  lattice KEM replaced by HQC).
- If the framework also needs **client authentication / update integrity** (signatures), that is
  a separate decision: either keep it out of scope (focus on the confidentiality layer), or use a
  non-code-based PQ signature (ML-DSA/Dilithium) and be explicit that only the KEM layer is
  code-based. **Decide this early** and state it clearly — do not try to "sign with HQC."

## 5. Tech stack

- **Python 3.10+**
- **liboqs / Open Quantum Safe** (`liboqs-python`, import `oqs`) — provides HQC (HQC-128/192/256)
  and Kyber/ML-KEM for the baseline. This is the core crypto dependency.
- **Flower** (`flwr`) — federated learning orchestration (clients + server).
- **PyTorch** — model training.
- Standard scientific stack: numpy, pandas, matplotlib.
- **Single GPU / CPU only. No special hardware. Zero budget.** Everything must run on Kaggle/Colab
  or a commodity machine.

## 6. Suggested repo structure

```
pqc-fl/
  README.md
  requirements.txt
  src/
    crypto/
      kem.py            # thin wrapper over oqs: keygen/encaps/decaps for HQC and Kyber
      masking.py        # pairwise-mask derivation + secure-aggregation masking
    aggregation/
      secure_agg.py     # the secure aggregation protocol (KEM-agnostic)
    federated/
      client.py         # Flower client (local train + mask)
      server.py         # Flower server (masked aggregation)
      fedavg.py         # plain FedAvg baseline
    models/
      cnn.py            # small CNN(s) for the datasets
    data/
      loaders.py        # FEMNIST / CIFAR-10 / IoT-IDS loaders + non-IID partitioning
    adversary/
      malicious.py      # malicious + colluding client simulation, dropout
    benchmark/
      metrics.py        # comm bytes, compute time, accuracy, robustness
  experiments/
    configs/            # yaml configs per run
    run.py              # entrypoint
  results/              # logs, csv, plots
```

## 7. Build plan (phases — each is a runnable milestone)

1. **Environment** — install liboqs-python, Flower, PyTorch; confirm `oqs` exposes HQC and Kyber;
   sanity-check encaps/decaps round-trip for both.
2. **Plain FL baseline** — FedAvg on FEMNIST + CIFAR-10 (non-IID partition). Record accuracy and
   raw communication (bytes/round/client) with no crypto.
3. **Lattice baseline** — secure aggregation with **Kyber** KEM + masking. This reproduces the
   status quo and is the comparison point.
4. **Code-based variant (the contribution)** — same protocol with **HQC** KEM. Then add the
   ciphertext-handling/compression step so the larger HQC payloads stay practical.
5. **Adversarial + robustness** — simulate malicious/colluding clients and dropout; measure
   accuracy degradation and the protocol's resilience for both KEMs.
6. **Benchmark + analyze** — head-to-head HQC vs Kyber on the metrics below; generate plots/tables.

## 8. Datasets (all public, no cost)

- **FEMNIST** (LEAF) — standard non-IID federated benchmark.
- **CIFAR-10** — image classification, partitioned non-IID across clients.
- **An IoT intrusion-detection set** (e.g., Edge-IIoTset) — matches the security framing and the
  domains used by related PQC-FL work.

## 9. Metrics to report

- **Communication:** bytes per round per client (model + key material + ciphertext overhead).
- **Computation:** keygen / encapsulate / decapsulate time; per-round wall-clock.
- **Utility:** test accuracy vs rounds (should match the plain baseline — crypto must not hurt accuracy).
- **Robustness:** accuracy under X% malicious/colluding clients; resilience to client dropout.
- **Security level:** post-quantum bits (128/192/256) for each configuration.

Headline comparison: **HQC vs Kyber** across all of the above — this is the diversity-vs-cost story.

## 10. Constraints carried from planning

- Software-only, single GPU, public datasets, zero cost (no hardware, no oscilloscope, no paid APIs).
- Keep the paper to **one sharp contribution** (code-based PQC in FL). Do **not** bolt on extra
  trend words (zero-trust, blockchain, agents) — they crowd the space and dilute focus.
- Target venues (Q1): IEEE Internet of Things Journal, IEEE TIFS, or IEEE TDSC.

## 11. References (finalized, peer-reviewed)

[1] National Institute of Standards and Technology, "Status Report on the Fourth Round of the NIST
Post-Quantum Cryptography Standardization Process," NIST IR 8545, Mar. 2025.

[2] X. Zhang, H. Deng, R. Wu, J. Ren, and Y. Ren, "PQSF: Post-quantum secure privacy-preserving
federated learning," *Scientific Reports*, vol. 14, no. 1, art. 23553, 2024,
doi: 10.1038/s41598-024-74377-6.

[3] X. Qin and R. Xu, "Efficient post-quantum cross-silo federated learning based on key
homomorphic pseudo-random function," *Mathematics*, vol. 13, no. 9, art. 1404, 2025,
doi: 10.3390/math13091404.

[4] P. Narsimhulu, P. Chithaluru, and R. Aluvalu, "Efficient post-quantum cryptographic signature
aggregation for low-latency distributed networks," *Journal of Information Security (EURASIP)*,
vol. 2026, art. 6, 2026, doi: 10.1186/s13635-026-00228-8.
