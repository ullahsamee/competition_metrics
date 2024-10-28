"""Compute ESM2 PLL given binder sequence."""

import math
import torch
import esm
import click

device = torch.device("cuda")

model, alphabet = esm.pretrained.esm2_t33_650M_UR50D()
batch_converter = alphabet.get_batch_converter()
model.eval()
model = model.to(device)


def compute_pll(sequence):
    data = [("protein", sequence)]
    batch_converter = alphabet.get_batch_converter()
    *_, batch_tokens = batch_converter(data)
    log_probs = []
    for i in range(len(sequence)):
        batch_tokens_masked = batch_tokens.clone()
        batch_tokens_masked[0, i + 1] = alphabet.mask_idx
        with torch.no_grad():
            token_probs = torch.log_softmax(
                model(batch_tokens_masked.to(device))["logits"], dim=-1
            )
        log_probs.append(token_probs[0, i + 1, alphabet.get_idx(sequence[i])].item())
    return math.fsum(log_probs)


@click.command()
@click.argument("aa_sequence")
def main(aa_sequence):
    pll = compute_pll(aa_sequence)
    print(f"PLL: {pll}")


if __name__ == "__main__":
    main()
