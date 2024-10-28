"""Extract metrics from ColabFold outputs."""

import os
import numpy as np
import json
import click


def get_metrics(
    output_folder, sequence_name, target_length=621
):  # the EGFR sequence has 621 residues
    files = os.listdir(output_folder)
    pae_file = f"{sequence_name}_predicted_aligned_error_v1.json"
    with open(os.path.join(output_folder, pae_file), "r") as f:
        pae = np.array(json.load(f)["predicted_aligned_error"])
    binder_len = (
        len(pae) - target_length
    )  # note that we are assuming that the binder always comes first in the sequence!
    pae_interaction = (
        pae[:binder_len, binder_len:].mean() + pae[binder_len:, :binder_len].mean()
    ) / 2
    scores = None
    for file in files:
        if file.startswith(f"{sequence_name}_scores_rank_001"):
            with open(os.path.join(output_folder, file), "r") as f:
                scores = json.load(f)
            break
    if scores is None:
        raise ValueError("No scores file found")
    iptm = scores["iptm"]
    return iptm, pae_interaction


@click.command()
@click.option(
    "--target_length", default=621, help="Length of the target protein (in amino acids)"
)
@click.argument("output_folder")
@click.argument("sequence_name")
def main(output_folder, sequence_name, target_length):
    iptm, pae_interaction = get_metrics(output_folder, sequence_name, target_length)
    print(f"IPTM: {iptm}")
    print(f"PAE interaction: {pae_interaction}")


if __name__ == "__main__":
    main()
