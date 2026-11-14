# SwiftAPI signed continuation results

Registration: [10.5281/zenodo.24209632](https://doi.org/10.5281/zenodo.24209632).
Predictions: [10.5281/zenodo.24206618](https://doi.org/10.5281/zenodo.24206618).
Source: [swiftapi-signed-continuation v1.0.0](https://github.com/theonlypal/swiftapi-signed-continuation/tree/v1.0.0),
commit `d7bf2b88db464696a394c6ddad0f73618c47be8d`.

The two registered populations contain 387 receipts: 11 PRIMARY and 376 SECONDARY.
All 13 arm-level class-count predictions match. All 387 receipts pass the SDK
receipt verifier and the full numerical boundary verifier in the supplied
verification records.

## PRIMARY: WITNESS_ONE

```text
[VALID] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [R]
[SIGNED_DENIAL] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [V0]
[MISSING_GRANT] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [V0]
[INVALID_SIGNATURE] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [V0]
[EXPIRED] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [V0]
[REUSED] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [V0]
[WRONG_SCOPE] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [V0]
[WRONG_REQUEST] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [V0]
[UNKNOWN_KEY] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [operational]
[MALFORMED_KEY] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [operational]
[REVOKED] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [1/1] [V0]
```

## SECONDARY: BANK_188

```text
[VALID] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [188/188] [R]
[MISSING_GRANT] [sharthokrayanpal/PCCG-2-Qwen3-4B@a3b952458a46b5547ba3cec7d03a37b395bed03a] [188/188] [V0]
```

## Evidence

`runs/PRIMARY/` and `runs/SECONDARY/` contain the raw receipts and their exact
request, prompt, input-token, grant, output and BF16-vector assets; authority
dispatches; prediction scores; ledger snapshots, reconciliations and finalization
records; per-receipt verification records; and independent verification reports.
`hardware/` contains the selected NVIDIA L4, EU-RO-1 host records.

The 385 model-executed responses have byte-identical stock and selected non-EOS
logits. Any changed logit is the native EOS entry, index 151645. The 196 V0
responses contain zero visible UTF-8 bytes and select native EOS at the first
decoding step through the learned gate. The 189 R responses contain visible text
and complete to native EOS. The two operational rejections have no model execution.

The release assets are `PRIMARY-evidence.tar.gz` and `SECONDARY-evidence.tar.gz`,
with matching `.sha256` sidecars. `ARCHIVES.json` pins their exact bytes. These
archives are release assets, not Git objects. The loose-file tree excludes
`run-approval.json`; the sealed archives include its approval identifier,
configuration hash and purpose. Each run's exact `SHA256SUMS` covers its sealed
archive, including that file. `PUBLIC_FILE_SHA256SUMS` covers the loose-file tree.

## Verify

Use Python 3.12. Put the two release archives in `release-assets/`. No API key,
signing seed, model weights, torch or network inference is needed. Package
installation uses PyPI; archive verification is offline.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install swiftapi-python==1.4.0
python verify.py --run PRIMARY --archive release-assets/PRIMARY-evidence.tar.gz
python verify.py --run SECONDARY --archive release-assets/SECONDARY-evidence.tar.gz
```

`verify.py` checks the pinned archive hash and every archive manifest entry,
uses the SDK to verify every receipt signature, authority object, asset hash,
stored-vector non-EOS identity, argmax and frozen class, and reconstructs class
counts against the hash-pinned author predictions. Its trust anchors are the
public runtime and authority keys pinned by source tag v1.0.0. It also checks the
ledger finalization hashes. The supplied full-verifier reports cover the
additional numerical gate calculation; this five-line block uses the SDK verifier,
not a model rerun.

## Scope

The grant check is trusted, unattested software. Signatures bind records; they
do not attest physical execution. The full numerical verifier recomputes the
small gate from captured scores, not the Qwen forward pass. Its float32 gate-state
absolute tolerance is `2^-21`; relative tolerance is zero. BF16 vectors, token
IDs, output bytes, signatures and asset hashes remain exact.

The authority ledger join is `JOINED_WITH_API_LIMITATIONS`: the governance listing
is unsigned and lacks a per-key signed census. The signed denial and the single
grant revocation have independently checked authority signatures. Non-revocation
at decision time remains a runtime report with captured feed checks.

These results concern one pinned PCCG-2 model, the registered question populations
and a software permission boundary. They do not establish universal security,
hosted-model continuation control or hardware attestation.
