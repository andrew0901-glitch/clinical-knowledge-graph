#!/usr/bin/env bash
# Rerun every audit lane from scratch on the public release files and check the headline numbers.
#   CLINICAL_KG_DATA=/path/to/clinical_kg_release_v0.2.1 audit/scripts/run_lanes.sh
# (fetch the files first: python audit/scripts/fetch_release.py). About 5 minutes, 20 GB RAM, 9 GB disk.
set -euo pipefail
cd "$(dirname "$0")/../.."
export CLINICAL_KG_DATA="${CLINICAL_KG_DATA:-$PWD/data/clinical_kg_release_v0.2.1}"
S=audit/lanes/scripts
for step in build lane2_medlineplus_english lane3_evidence_maps lane4_osteosarcoma lane5_paper_numbers \
            lane1_trial_landscape lane3_crosscheck_companion headline_numbers; do
  echo "=== $step"
  python3 "$S/$step.py"
done
echo "=== Zenodo bundle cross-check"
python3 audit/scripts/verify_zenodo_bundles.py
echo "=== record hashes"
python3 "$S/lanes_manifest.py"
