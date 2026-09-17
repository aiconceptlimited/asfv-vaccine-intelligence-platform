#!/usr/bin/env bash

set -u

PROJECT="$HOME/asfv_vaccine_platform"
OUT="$PROJECT/audit/environment"
SW="$PROJECT/audit/software"

mkdir -p "$OUT" "$SW"

echo "============================================================"
echo "ASFV VACCINE PLATFORM - ENVIRONMENT/SOFTWARE AUDIT"
echo "Date: $(date -Is)"
echo "============================================================"
echo

# ------------------------------------------------------------
# SYSTEM
# ------------------------------------------------------------

{
echo "=== HOST ==="
hostnamectl 2>/dev/null || hostname
echo

echo "=== OS ==="
cat /etc/os-release 2>/dev/null
echo

echo "=== KERNEL ==="
uname -a
echo

echo "=== CPU ==="
lscpu 2>/dev/null
echo

echo "=== MEMORY ==="
free -h
echo

echo "=== STORAGE ==="
df -hT
echo

echo "=== MOUNTED FILESYSTEMS ==="
findmnt 2>/dev/null
echo

echo "=== UPTIME ==="
uptime
} > "$OUT/system_environment.txt" 2>&1

# ------------------------------------------------------------
# NETWORK INFORMATION
# Avoid private credentials / secrets.
# ------------------------------------------------------------

{
echo "=== NETWORK INTERFACES ==="
ip -br addr 2>/dev/null
echo

echo "=== ROUTING ==="
ip route 2>/dev/null
} > "$OUT/network.txt" 2>&1

# ------------------------------------------------------------
# PYTHON
# ------------------------------------------------------------

{
echo "=== PYTHON ==="
command -v python3 || true
python3 --version 2>/dev/null || true
python3 -c 'import sys; print(sys.executable); print(sys.version)' 2>/dev/null || true
echo

echo "=== PIP ==="
python3 -m pip --version 2>/dev/null || true
echo

echo "=== BIOPYTHON ==="
python3 - <<'PY'
try:
    import Bio
    print("Biopython:", Bio.__version__)
except Exception as e:
    print("Biopython: NOT AVAILABLE")
    print(type(e).__name__, str(e))
PY
} > "$SW/python.txt" 2>&1

# ------------------------------------------------------------
# CONDA / MAMBA
# ------------------------------------------------------------

{
echo "=== CONDA ==="
command -v conda || true
conda --version 2>/dev/null || true
echo

echo "=== MAMBA ==="
command -v mamba || true
mamba --version 2>/dev/null || true
echo

echo "=== ENVIRONMENTS ==="
conda env list 2>/dev/null || true
} > "$SW/conda_mamba.txt" 2>&1

# ------------------------------------------------------------
# WORKFLOW SYSTEM
# ------------------------------------------------------------

{
echo "=== SNAKEMAKE ==="
command -v snakemake || true
snakemake --version 2>/dev/null || true

echo
echo "=== NEXTFLOW ==="
command -v nextflow || true
nextflow -version 2>/dev/null || true
} > "$SW/workflow_engines.txt" 2>&1

# ------------------------------------------------------------
# CONTAINERS
# ------------------------------------------------------------

{
echo "=== DOCKER ==="
command -v docker || true
docker --version 2>/dev/null || true

echo
echo "=== APPTAINER ==="
command -v apptainer || true
apptainer --version 2>/dev/null || true

echo
echo "=== SINGULARITY ==="
command -v singularity || true
singularity --version 2>/dev/null || true
} > "$SW/containers.txt" 2>&1

# ------------------------------------------------------------
# BIOINFORMATICS TOOLS
# ------------------------------------------------------------

TOOLS=(
  seqkit
  mafft
  clustalo
  trimAl
  iqtree2
  iqtree
  blastp
  mmseqs
  hmmscan
  hmmsearch
  signalp6
  deepTMHMM
  gromacs
  pymol
  chimerax
  mysql
  mysqldump
  git
  node
  npm
)

{
echo "=== TOOL INVENTORY ==="
echo "Date: $(date -Is)"
echo

for t in "${TOOLS[@]}"; do
    echo "------------------------------------------------------------"
    echo "TOOL: $t"
    echo "PATH: $(command -v "$t" 2>/dev/null || echo NOT_FOUND)"

    if command -v "$t" >/dev/null 2>&1; then
        "$t" --version 2>&1 | head -5 || true
    fi
    echo
done
} > "$SW/bioinformatics_tool_inventory.txt" 2>&1

# ------------------------------------------------------------
# PYTHON PACKAGES
# ------------------------------------------------------------

python3 - <<'PY' > "$SW/python_packages.txt" 2>&1
import importlib.util

packages = [
    "pandas",
    "numpy",
    "scipy",
    "sklearn",
    "Bio",
    "streamlit",
    "dash",
    "plotly",
    "sqlalchemy",
    "pymysql",
    "mysql",
    "snakemake",
    "pymoo",
    "ortools",
    "xgboost",
    "torch",
]

print("=== PYTHON PACKAGE AVAILABILITY ===")

for p in packages:
    spec = importlib.util.find_spec(p)
    print(f"{p:15s} : {'AVAILABLE' if spec else 'NOT_FOUND'}")

    if spec:
        try:
            mod = __import__(p)
            print(" " * 4 + "version:", getattr(mod, "__version__", "unknown"))
        except Exception as e:
            print(" " * 4 + "import error:", type(e).__name__, str(e))
PY

# ------------------------------------------------------------
# GIT
# ------------------------------------------------------------

if [ -d "$PROJECT/.git" ]; then
{
echo "=== GIT STATUS ==="
cd "$PROJECT"
git status --short
echo

echo "=== CURRENT COMMIT ==="
git rev-parse HEAD 2>/dev/null || true
echo

echo "=== BRANCH ==="
git branch --show-current 2>/dev/null || true
echo

echo "=== RECENT COMMITS ==="
git log --oneline -10 2>/dev/null || true
} > "$OUT/git_status.txt" 2>&1
else
echo "No .git directory found" > "$OUT/git_status.txt"
fi

# ------------------------------------------------------------
# SERVICES / PROCESSES
# ------------------------------------------------------------

{
echo "=== SYSTEMD SERVICES RELEVANT TO PROJECT ==="
systemctl list-units --type=service --all 2>/dev/null \
  | grep -Ei 'dash|streamlit|gunicorn|nginx|apache|mysql|mariadb|docker|snakemake' || true

echo
echo "=== RUNNING PROCESSES RELEVANT TO PROJECT ==="
ps aux 2>/dev/null \
  | grep -Ei 'dash|streamlit|gunicorn|nginx|apache|mysql|mariadb|snakemake' \
  | grep -v grep || true
} > "$OUT/services_processes.txt" 2>&1

# ------------------------------------------------------------
# PROJECT FILESYSTEM SUMMARY
# ------------------------------------------------------------

{
echo "=== TOP-LEVEL PROJECT ==="
cd "$PROJECT"
find . -maxdepth 1 -mindepth 1 -printf '%y %p\n' | sort

echo
echo "=== DIRECTORY TREE (DEPTH 3) ==="
find . -maxdepth 3 -type d -printf '%p\n' | sort

echo
echo "=== FILE COUNTS BY EXTENSION ==="
find . -type f -printf '%f\n' \
  | awk '
    BEGIN {FS="."}
    NF==1 {count["[no_extension]"]++; next}
    {ext=$NF; count[ext]++}
    END {
      for (e in count) print e, count[e]
    }' \
  | sort

echo
echo "=== LARGE FILES >100 MB ==="
find . -type f -size +100M -printf '%s %p\n' 2>/dev/null | sort -nr

echo
echo "=== RECENTLY MODIFIED FILES ==="
find . -type f -printf '%T@ %p\n' \
  | sort -nr \
  | head -100
} > "$PROJECT/audit/filesystem/project_inventory.txt" 2>&1

# ------------------------------------------------------------
# CHECKSUMS OF CRITICAL CONTROL FILES
# ------------------------------------------------------------

{
echo "=== CONTROL FILE CHECKSUMS ==="

for f in \
  config/pipeline.yaml \
  config/sla.yaml \
  config/*.yaml \
  config/*.yml \
  FINAL_REPRODUCIBILITY_RECORD.md \
  C05_H06_B241_final.fasta \
  final_candidate_ranking.tsv
do
    [ -f "$f" ] && sha256sum "$f"
done
} > "$OUT/control_file_sha256.txt" 2>&1

echo "Audit completed."
echo "Environment results: $OUT"
echo "Software results:    $SW"
echo "Filesystem results:  $PROJECT/audit/filesystem"
