# create a list of all WPs with more than one coauthor
# whose coauthors are consultative that year
#
# also produces handy files:
# - wp_infos_{date}.csv  
#   - every WP from ATS and ATAAD
#   - also every revision I could find
# - wp_infos_merged_revisions_{date}.csv
#   - every WP as above but revisions info merged

import os
import pandas as pd
import datetime
from pathlib import Path

# parameters
# ---

raw_data_dir = Path(os.environ.get("DATA_RAW"), ".")
processed_data_dir = Path(os.environ.get("DATA_PROCESSED", "."))
ats_dir = raw_data_dir / "wp_infos_from_ats"
ataad_path = raw_data_dir / "wps_missing_from_ats/wps_missing.csv"


# get, merge, and clean WP info
# ---

# get ATS data
if not ats_dir.exists():
    raise FileNotFoundError(f"Directory not found: {ats_dir}. Check your .envrc.")
ats_fnames = [f for f in ats_dir.glob("*.csv")]
list_of_dfs = [pd.read_csv(ats_dir / ats_fname) for ats_fname in ats_fnames]
df_ats = pd.concat(list_of_dfs, ignore_index=True)

# get data mainly from ATAAD
if not ataad_path.exists():
    raise FileNotFoundError(f"File not found: {ataad_path}. Check your .envrc.")
df_ataad = pd.read_csv(ataad_path)
df_ataad = df_ataad[~df_ataad["is_true_gap"]][df_ats.columns]

# merge and clean
df = pd.concat([df_ats, df_ataad])
df.sort_values(by=["meeting_year", "paper_number", "paper_revision"], inplace=True)
df.reset_index(drop=True, inplace=True)

# apply corrections (see /scripts/check/data_raw/wp_change_between_revisions.py)
# ---

# get corrections data
corrns_path = processed_data_dir / "corrections_by_hand/wp_infos.csv"
if not corrns_path.exists():
    raise FileNotFoundError(f"File not found: {corrns_path}.")

df_corrns = pd.read_csv(corrns_path)[[
    "meeting_year",
    "paper_number",
    "paper_revision",
    "delete_row",
    "incorrect_columns",
    "corrected_values",
]]

# make corrections to df based on info in each row of df_corrns
for index, row in df_corrns.iterrows():
    mask = (
        (df["meeting_year"] == row["meeting_year"])
        & (df["paper_number"] == row["paper_number"])
        & (df["paper_revision"] == row["paper_revision"])
    )
    if row["delete_row"]:
        df.drop(df[mask].index[0], inplace=True)
    else:
        incorrect_columns = row["incorrect_columns"].split(" || ")
        corrected_values = row["corrected_values"].split(" || ")
        for ic, cv in zip(incorrect_columns, corrected_values):
            original_type = df[ic].dtype
            df.loc[mask, ic] = pd.Series([cv]).astype(original_type).iloc[0]

# write this as a CSV with the date bc it will be handy to have for other reasons
date = datetime.date.today()
df.to_csv(
    processed_data_dir
    / f"compile_infos/wp_infos_{date.year}_{date.month}_{date.day}.csv",
    index=False,
)
# 2500 WPs


# compress WPs with multiple revisions
# ---

# take the union of all coauthors of every revision

# get (year, WP number) of each paper with revisions
df_rev = df[df["paper_revision"] > 0]
has_rev = set(
    [
        (meeting_year, paper_number)
        for meeting_year, paper_number in zip(
            df_rev["meeting_year"], df_rev["paper_number"]
        )
    ]
)

# create a column indicating if this WP has revisions or not
df["has_revisions"] = [
    v in has_rev for v in list(zip(df["meeting_year"], df["paper_number"]))
]

# create a new dataframe that merges their parties into one list,
# and uses the first paper for the title, etc.

# initialise with all entries with no revisions
list_of_dfs = [df[~df["has_revisions"]]]

for meeting_year, paper_number in has_rev:
    df_subset = df[
        (df["meeting_year"] == meeting_year) & (df["paper_number"] == paper_number)
    ]

    partiesS = set(df_subset["parties"])
    partyV = list()
    for parties in partiesS:
        partyV += parties.split(" | ")
    parties_new = " | ".join(sorted(set(partyV)))

    # create new dataframe from first entry and new parties list
    df_new = df_subset.head(1).copy()
    df_new.reset_index(drop=True, inplace=True)
    df_new.loc[0, "parties"] = parties_new

    # append
    list_of_dfs.append(df_new)

df_merged = pd.concat(list_of_dfs)

# only keep columns that make sense after merging revisions
columns_to_keep = [
    "meeting_year",
    "meeting_type",
    "meeting_number",
    "meeting_name",
    "paper_type",
    "paper_number",
    "has_revisions",
    "paper_name",
    "agendas",
    "parties",
    "url",
]
df_merged = df_merged[columns_to_keep]

# and make their column names make sense
rename_columns = {
    "paper_name": "one_revision_name",
    "url": "one_revision_url",
}
df_merged.rename(columns=rename_columns, inplace=True)

# write this as a CSV with the date bc it will be handy to have for other reasons
df_merged.sort_values(by=["meeting_year", "paper_number"], inplace=True)
df_merged.reset_index(drop=True, inplace=True)
df_merged.to_csv(
    processed_data_dir
    / f"compile_infos/wp_infos_merged_revisions_{date.year}_{date.month}_{date.day}.csv",
    index=False,
)


# create CSV with only WPs with more than 1 consultative country as authors
# ---

# year consultative countries joined
df_consult = pd.read_csv(raw_data_dir / "year_countries_consultative.csv")
countries_consulative_in_year = lambda year: list( # noqa
    df_consult[df_consult["year_joined"] <= year]["country"]
)

# cut back to only WPs with more than one author
df_subset = df_merged[
    df_merged["parties"].astype(str).str.contains(" | ", regex=False)
].copy()

# trim party list to only countries that were consultative in that year
df_subset["consult_countries"] = [
    " | ".join(
        [
            party
            for party in parties.split(" | ")
            if party in countries_consulative_in_year(meeting_year)
        ]
    )
    for meeting_year, parties in zip(df_subset["meeting_year"], df_subset["parties"])
]

# cut back to only WPs with more than 1 consultative-country author
df_subset = df_subset[
    df_subset["consult_countries"].astype(str).str.contains(" | ", regex=False)
]

df_out = df_subset[
    [
        "meeting_year",
        "meeting_type",
        "meeting_number",
        "meeting_name",
        "paper_type",
        "paper_number",
        "consult_countries",
    ]
]
df_out.to_csv(
    processed_data_dir / "compile_infos/wp_consult_coauthors.csv", index=False
)
