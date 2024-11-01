# Adaptyv Bio Competition Metrics

In round 2 of our [protein design competition](https://design.adaptyvbio.com/) we are using a rank average of three metrics: iPTM, ESM PLL and PAE interaction.
Here you can find some implementation details on how to compute those metrics for your proteins, as well as our rationale with going with these metrics and aggregation method.

# Metrics Rationale

After our [call for suggestions and input](https://x.com/adaptyvbio/status/1841863101408280651), we internally discussed scores like PRODIGY, molecular dynamics simulations and other ideas and also sought out (and received) feedback about their generality.

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

## Running AlphaFold2

iPTM and PAE interaction are both derived from the output of AlphaFold2. More specifically, in our pipeline we use the ColabFold implementation.

To generate structure predictions with the same parameters as we do, you can use the following command.

```bash
colabfold_batch input.fasta output_dir --num-recycle 3 --num-seeds 3 --num-models 5 --templates
```

Here `input.fasta` is the input file with the protein sequences and `output_dir` is the directory where the predictions will be saved. Down the line we use the output that is ranked the highest by the ColabFold pipeline.

In the fasta file, each entry should have the binder and the target sequences, separated by `:`. In our processing script we assume that the binder sequence always comes first.

This command will use the ColabFold server to run MSA predictions. In case you are evaluating a large number of proteins, it is recommended to set up your own MSA pipeline, as described [here](https://github.com/YoshitakaMo/localcolabfold). If you do that, you will need to run those two commands (the former is run on your MSA server and the latter on a machine that has a GPU).

```bash
colabfold_search input.fasta database msa_dir --db2 pdb100_230517 --use-templates 1
colabfold_batch {NAME}.a3m output_dir --num-recycle 3 --num-seeds 3 --num-models 5 --templates --local-pdb-path {MOUNT_PATH}/20240101/pub/pdb/data/structures/divided/mmCIF --pdb-hit-file {NAME}_pdb100_230517.m8
```

Here `{NAME}.a3m` and `{NAME}_pdb100_230517.m8` are the MSA and template files generated by `colabfold_search` for a single sequence and `msa_dir` and `output_dir` are the directories where the outputs will be saved. Finally, `{MOUNT_PATH}` is the path to the PDB database (`s3://pdbsnapshots/`). The database can be mounted, for instance, with [`s3fs`](https://github.com/s3fs-fuse/s3fs-fuse).

## Extracting AlphaFold2 metrics

You can find a script for extracting iPTM and PAE interaction from the AlphaFold2 predictions with our python script. Note that this script assumes that the binder sequence always comes before the target sequence in the input fasta file.

```bash
python compute_af2_metrics.py output_dir {NAME} --target_length {TARGET_LENGTH}
```

Here `{NAME}` is the name of the protein. Most of the time it is the name you provided in the input fasta file. The `output_dir` parameter should point to a folder generated with commands from the previous section. The script will output the iPTM and PAE interaction metrics for the protein. The `--target_length` flag is optional and should be used if the target sequence is not EGFR (as in our competition).

## Computing ESM PLL

The ESM PLL metric can be computed with a separate script. This assumes that your machine has a GPU.

```bash
python compute_pll.py {BINDER_SEQUENCE}
```

Here `{BINDER_SEQUENCE}` is the amino acid sequence of the binder protein. The script will output the ESM PLL metric for this sequence.

## Rank average

To compute the final value, we rank the designs on each of the three metrics separately and then average the ranks. Ties are resolved by averaging the ranks of the tied submissions. The lower the rank average, the better the submission.

We have added a helper script that takes a csv of metrics and computes a rank average. 

```bash
python rank.py metrics.csv --asc esm_pll --asc iptm --desc pae_interaction --save_path ranked_metrics.csv
```
