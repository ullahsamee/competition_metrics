import pandas as pd
import click
from pandas.api.types import is_numeric_dtype

def add_rank(df, asc=None, desc=None):
    if asc is None:
        asc = []
    if desc is None:
        desc = []
    if len(asc) == 0 and len(desc) == 0:
        asc = [x for x in df.columns if is_numeric_dtype(df[x])]
    for col in asc:
        df[f"{col}_rank"] = df[col].rank(ascending=True)
    for col in desc:
        df[f"{col}_rank"] = df[col].rank(ascending=False)
    df["rank"] = sum([df[f"{col}_rank"] for col in asc + desc]) / len(asc + desc)
    df = df.sort_values(["rank"])
    return df

@click.command
@click.option("--asc", multiple=True, type=str, help="Column names to sort by (ascending).")
@click.option("--desc", multiple=True, type=str, help="Column names to sort by (descending).")
@click.option("--save_path", type=str, help="Path to save the table with the rank.")
@click.argument("input_path")
def rank(asc, desc, save_path, input_path):
    df = pd.read_csv(input_path)
    df = add_rank(df, asc=asc, desc=desc)
    if save_path is not None:
        df.to_csv(save_path)
    else:
        print(df)


if __name__ == "__main__":
    rank()