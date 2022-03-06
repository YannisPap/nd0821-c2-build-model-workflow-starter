#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import os
from pathlib import Path

import pandas as pd
import wandb

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    # artifact_local_path = run.use_artifact(args.input_artifact).file()

    logger.info("Downloading artifact")
    artifact = run.use_artifact(args.input_artifact)
    artifact_local_path = artifact.file()

    logger.info("Removing outliers based on price")
    df = pd.read_csv(filepath_or_buffer=artifact_local_path)
    df = df.loc[
        df["price"].between(left=args.min_price, right=args.max_price)
        & df["longitude"].between(left=-74.25, right=-73.50)
        & df["latitude"].between(left=40.5, right=41.2)
    ]

    file_path = Path("artifacts", "processed_data.csv")
    df.to_csv(file_path, index=False)

    artifact = wandb.Artifact(
        name=args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )

    artifact.add_file(file_path)

    logger.info("Logging artifact")
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Fully-qualified name for the input artifact containing data before "
        "applying any cleaning process.",
        required=True,
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="Name for the output artifact containing the cleaned data.",
        required=True,
    )

    parser.add_argument(
        "--output_type", type=str, help="The type of the output artifact", required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="Description of the output artifact.",
        required=True,
    )

    parser.add_argument(
        "--min_price",
        type=int,
        help="The minimum allowed price of a listing.",
        required=True,
    )

    parser.add_argument(
        "--max_price",
        type=int,
        help="The maximum allowed price of a listing.",
        required=True,
    )

    args = parser.parse_args()

    go(args)
