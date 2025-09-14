# Metrics Rationale

Please check [Protein Design Competition](https://design.adaptyvbio.com/), we internally discussed scores like PRODIGY, molecular dynamics simulations and other ideas and also sought out (and received) feedback about their generality.

Our goal was to find "better" metrics that would in particular help us to choose (and the participants to design) sequences that are likely to express and be measurable, since the "high" rate of non-expression was a source of frustration for some round 1 participants.

In the end, we went with the following score

$s(seq)=\frac{1}{3}\left(r_\uparrow\left(iPTM\left(seq\right)\right)+r_\downarrow\left(PAE\left(seq\right)\right)+r_\uparrow\left(pLL\left(seq\right)\right)\right)$

with

- $r_{\lbrace \uparrow /  \downarrow \rbrace}(\cdot)$ being ascending/descending ranks (using fractional ranking to deal with ties)
- $iPTM$ being AF2 interface predicted TM-score as in [Evans et al.2022](https://www.biorxiv.org/content/10.1101/2021.10.04.463034v2)
- $PAE$ being AF2 predicted alignment error averaged over inter-chain residue pairs (as in e.g. [specifically here](https://github.com/nrbennet/dl_binder_design), [specifically here](https://github.com/nrbennet/dl_binder_design/blob/cafa3853ac94dceb1b908c8d9e6954d71749871a/af2_initial_guess/predict.py#L197)).
- $pLL$ being the [Pseudo-log-likelihood](https://en.wikipedia.org/wiki/Pseudolikelihood) of the `esm2_t33_650M_UR50D` model

due to considerations of evaluation time (ruling out MD based metrics), simplicity while still providing a "good enough" metric allowing for direct optimization.

$iPTM$ was added as a measure of "global" structure quality, while we hope that $pLL$ will help bias things towards expressible targets.
Despite the latter possibly being a [spurious correlation](https://x.com/adaptyvbio/status/1844456050726174751), most experts we asked said that everything else being equal, low $pLL$ is probably a good filtering criteria for unexpressible sequences.

Unlike the first round of the competition, we compute all AlphaFold2 derived metrics using templates taking inspiration from https://github.com/nrbennet/dl_binder_design.
We made this choice since we received feedback that this improves the quality of the predictions.
This and the inclusion of the $pLL$ _might_ favour more "natural" designs or those closer to existing sequences over denovo design.
However, some bias is unavoidable in the absence of a clearly winning metric. Combining this with the fact that we did not receive any suggestions for clearly better alternatives made us bite this particular bullet.
As we state in the [evaluation criteria](https://design.adaptyvbio.com/)

> 100 additional designs will be chosen for their novelty, creativity in the design process or other interesting factors.

so we will use this flexibility to ensure some "interesting" denovo designs are chosen to counteract this possible bias, if it occurs.

## Installation

See [here](https://github.com/sokrypton/ColabFold?tab=readme-ov-file) for instructions on how to install the ColabFold pipeline. We use it to generate structure predictions.

To run the python scripts in this repository, you will need to install the requirements with pip.

```bash
python -m pip install -r requirements.txt
```

# After LocalColabFold SETUP
A comprehensive guide for protein design analysis using ColabFold and associated metrics tools.

## Prerequisites

- ColabFold successfully installed
- `competition_metrics-main` clone repo
- Python environment with required dependencies

## Single Protein Design Analysis

### Step 1: Prepare Input File

Create a FASTA file in your home directory:

```bash
# Create input.fasta anywhere in home directory
nano input.fasta
```

```fasta
>MyProteinDesign
Bindersequence:targetproteinseuqence
```

### Step 2: Run ColabFold Prediction

Execute the following command in your terminal:

```bash
colabfold_batch input.fasta output_dir --num-recycle 3 --num-seeds 3 --num-models 5 --templates
```

**Parameters:**
- `--num-recycle 3`: Number of recycling iterations
- `--num-seeds 3`: Number of random seeds for diversity
- `--num-models 5`: Number of models to generate
- `--templates`: Use template-based modeling

### Step 3: Compute AF2 Metrics

Navigate to the metrics directory and run:

```bash
cd competition_metrics-main
python compute_af2_metrics.py /home/ullah/output_dir MyProteinDesign --target_length 118
```

**Expected Output:**
```
IPTM: 0.87
PAE interaction: 6.471416075360901
```

> **Important:** Copy and save these values for your records.

### Step 4: Compute PLL Values

Calculate the Protein Language Model likelihood:

```bash
python compute_pll.py BINDER_SEQUENCE
```

**Expected Output:**
```
PLL: -126.43344932794571
```

> **Important:** Copy and save this PLL value.

## Batch Processing Multiple Designs

### Step 1: Batch ColabFold Prediction

Run batch prediction on multiple sequences:

```bash
colabfold_batch input.fasta ../designs_output --num-recycle 3 --num-seeds 3 --num-models 5 --templates
```

### Step 2: Configure Extraction Script

Edit the `extract_pae_iptm.sh` script with the following parameters:

```bash
INPUT_FASTA="designs_input/input.fasta"        # Batch input FASTA file
OUTPUT_DIR="designs_output"                    # ColabFold output directory
METRICS_FILE="designs_input/metrics.csv"       # Generated metrics file
TARGET_LENGTH=118                              # Target sequence length
```

### Step 3: Execute Batch Extraction

```bash
bash extract_pae_iptm.sh
```

This will generate a CSV file containing iPTM and PAE values for all designs.

### Step 4: Rank Designs

Sort and rank designs based on multiple criteria:

```bash
python rank.py metrics.csv --asc esm_pll --asc iptm --desc pae_interaction --save_path ranked_metrics.csv
```

**Ranking Criteria:**
- `--asc esm_pll`: Ascending order for ESM PLL (lower is better)
- `--asc iptm`: Ascending order for iPTM (higher values rank better)
- `--desc pae_interaction`: Descending order for PAE interaction (lower is better)

## Output Files

### Single Analysis
- Predicted structures in `output_dir/`
- iPTM and PAE values (CLI output)
- PLL value (CLI output)

### Batch Analysis
- `metrics.csv`: Raw metrics for all designs
- `ranked_metrics.csv`: Sorted and ranked designs

## Metrics Interpretation

| Metric | Description | Better Value |
|--------|-------------|--------------|
| **iPTM** | Interface Predicted Template Modeling confidence | Higher (closer to 1.0) |
| **PAE Interaction** | Predicted Aligned Error for protein interactions | Lower |
| **PLL** | Protein Language Model likelihood | Context-dependent |

## Tips for Success

1. **File Paths**: Ensure all file paths are correct and accessible
2. **Target Length**: Verify the target protein length is accurate
3. **Sequence Format**: Double-check FASTA formatting
4. **Resources**: Monitor computational resources for large batch jobs
5. **Backup**: Save important output files and metrics

## Troubleshooting

### Common Issues
- **Path errors**: Verify all directory paths exist
- **Permission errors**: Check file/directory permissions
- **Memory issues**: Reduce batch size for large datasets
- **Template errors**: Ensure template databases are accessible

### Support
For additional help:
- Check ColabFold documentation
- Review log files in output directories
- Verify input file formatting
