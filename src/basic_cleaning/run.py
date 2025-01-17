#!/usr/bin/env python
"""
Perform basic cleaning on the data and save the results in Weights & Biases
"""
import argparse
import logging
import os
import wandb

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # particular version of the artifact
    artifact_local_path = run.use_artifact(args.input_artifact).file()

    df = pd.read_csv(artifact_local_path)

    #Drop outliers
    logger.info(("Dropping outliers"))
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()

    #Convert last_review to datetime
    logger.info("Converting reviews to datetime")
    df['last_review'] = pd.to_datetime(df["last_review"])

    #Drop unproper geolocation
    logger.info("Drop unproper geolocations")
    idx = df['longitude'].\
        between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    filename = "clean_sample.csv"
    df.to_csv(filename, index=False)

    artifact = wandb.Artifact(
        name=args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file(filename)

    logger.info("Logging artifact")
    run.log_artifact(artifact)

    os.remove(filename)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This step cleans the data")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Fully qualified name for the inpıt artifact",
        required=True,
    )

    parser.add_argument(
        "--output_artifact", 
        type=str,
        help="Name for the W&B artifact that will be created",
        required=True,
    )

    parser.add_argument(
        "--output_type", 
        type=str, 
        help="Type of the artifact to create",
        required=True,
    )

    parser.add_argument(
        "--output_description", 
        type=str,
        help="Description for the artifact to create",
        required=True,
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum price",
        required=True,
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum price",
        required=True,
    )


    args = parser.parse_args()

    go(args)
