from __future__ import annotations

import argparse
import logging
import time
from typing import Final

import pandas as pd
import requests

DATASET_URLS: Final[dict[str, str]] = {
    "intakes": "https://data.austintexas.gov/resource/wter-evkm.json",
    "outcomes": "https://data.austintexas.gov/resource/9t4d-g238.json",
}

INTAKE_COLUMN_ORDER: Final[list[str]] = [
    "animal_id",
    "name",
    "intake_datetime",
    "found_location",
    "intake_type",
    "intake_condition",
    "animal_type",
    "sex_upon_intake",
    "age_upon_intake",
    "breed",
    "color",
]

OUTCOME_COLUMN_ORDER: Final[list[str]] = [
    "animal_id",
    "name",
    "date_of_birth",
    "outcome_datetime",
    "outcome_type",
    "outcome_subtype",
    "animal_type",
    "sex_upon_outcome",
    "age_upon_outcome",
    "breed",
    "color",
]


def fetch_all_rows(
    url: str,
    limit: int = 1000,
    max_retries: int = 5,
    sleep_seconds: int = 2,
    timeout_seconds: int = 60,
) -> pd.DataFrame:
    all_rows: list[dict] = []
    offset = 0

    while True:
        batch = None

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(
                    url,
                    params={"$limit": limit, "$offset": offset},
                    timeout=timeout_seconds,
                )
                response.raise_for_status()
                batch = response.json()
                break
            except requests.exceptions.RequestException as exc:
                logging.warning(
                    "Request failed for offset=%s attempt=%s/%s: %s",
                    offset,
                    attempt,
                    max_retries,
                    exc,
                )
                if attempt < max_retries:
                    time.sleep(sleep_seconds)
                else:
                    raise

        if batch is None:
            raise RuntimeError(f"Failed to fetch data for offset={offset}")

        logging.info("Fetched batch: offset=%s rows=%s", offset, len(batch))

        if not batch:
            break

        all_rows.extend(batch)

        if len(batch) < limit:
            break

        offset += limit

    df = pd.DataFrame(all_rows)
    logging.info("Finished fetch: rows=%s cols=%s", df.shape[0], df.shape[1])
    return df


def normalize_datetime_column(
    df: pd.DataFrame,
    datetime_col: str,
    new_datetime_col: str,
    local_tz: str = "America/Chicago",
) -> pd.DataFrame:
    df = df.copy()

    raw = df[datetime_col].astype("string")
    has_tz = raw.str.contains(r"(?:Z|[+-]\d{2}:\d{2})$", na=False)

    aware = pd.to_datetime(raw[has_tz], errors="coerce", utc=True)

    naive = pd.to_datetime(raw[~has_tz], errors="coerce")
    naive = naive.dt.tz_localize(
        local_tz,
        ambiguous="NaT",
        nonexistent="shift_forward",
    ).dt.tz_convert("UTC")

    combined = pd.Series(index=df.index, dtype="datetime64[ns, UTC]")
    combined.loc[has_tz] = aware
    combined.loc[~has_tz] = naive

    df[new_datetime_col] = combined
    df = df.drop(columns=[datetime_col])

    return df


def clean_animal_dataset(df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    df = df.copy()

    if "animal_id" in df.columns:
        df["animal_id"] = df["animal_id"].astype("string")

    if dataset == "intakes":
        df = normalize_datetime_column(
            df=df,
            datetime_col="datetime",
            new_datetime_col="intake_datetime",
        )

        drop_cols = [c for c in ["datetime2"] if c in df.columns]
        if drop_cols:
            df = df.drop(columns=drop_cols)

        existing = [c for c in INTAKE_COLUMN_ORDER if c in df.columns]
        remaining = [c for c in df.columns if c not in existing]
        df = df[existing + remaining]

    elif dataset == "outcomes":
        df = normalize_datetime_column(
            df=df,
            datetime_col="datetime",
            new_datetime_col="outcome_datetime",
        )

        drop_cols = [c for c in ["monthyear"] if c in df.columns]
        if drop_cols:
            df = df.drop(columns=drop_cols)

        existing = [c for c in OUTCOME_COLUMN_ORDER if c in df.columns]
        remaining = [c for c in df.columns if c not in existing]
        df = df[existing + remaining]

    else:
        raise ValueError(f"Unsupported dataset: {dataset}")

    return df


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch, clean, and write Austin Animal Center dataset to Parquet."
    )
    parser.add_argument(
        "--dataset",
        required=True,
        choices=["intakes", "outcomes"],
        help="Dataset to ingest.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output parquet path, e.g. intakes.parquet",
    )
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument("--sleep-seconds", type=int, default=2)
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    args = parse_args()
    url = DATASET_URLS[args.dataset]

    logging.info("Starting ingestion for dataset=%s", args.dataset)
    logging.info("Source URL=%s", url)

    df_raw = fetch_all_rows(
        url=url,
        limit=args.limit,
        max_retries=args.max_retries,
        sleep_seconds=args.sleep_seconds,
    )
    df_clean = clean_animal_dataset(df_raw, dataset=args.dataset)

    null_count = (
        df_clean["intake_datetime"].isna().sum()
        if args.dataset == "intakes"
        else df_clean["outcome_datetime"].isna().sum()
    )

    logging.info("Cleaned dataframe shape=%s", df_clean.shape)
    logging.info("Null datetimes after cleaning=%s", null_count)

    df_clean.to_parquet(args.output, index=False)
    logging.info("Wrote parquet file: %s", args.output)


if __name__ == "__main__":
    main()