# There is data missing from the ATS website about Working Papers. As
# a first approximation, find gaps in the WP-number sequences
# (e.g., WP1, WP2, WP4, ...)

import os
import pandas as pd
import numpy as np


# parameters
# ---

# paths
raw_data_dir = os.environ.get("DATA_RAW")


# find the gaps in WP numbers
# ---

# ATADD (UTas website) provides a partial collection of the maximum
# WP number at each ATCM
fname = os.path.join(raw_data_dir, "list_of_docs/list_of_docs.csv")
df = pd.read_csv(fname)
df = df[~np.isnan(df["max_wp_nbr"])]
max_wp_nbrD = {year: int(nbr) for year, nbr in zip(df["year"], df["max_wp_nbr"])}

# list of all CSV files containin wp information from ATS website
wps_fnames = os.listdir(os.path.join(raw_data_dir, "wp_infos_from_ats"))

# for each CSV, find gaps in the working-paper-number sequence

# gaps in the wp-sequence
missingD = dict() # {year_1: "missing_nbr_1 | missing_nbr_2 | ...", year_2: ...}

for wps_fname in wps_fnames:
    # import wp info as a dataframe
    file_path = os.path.join(raw_data_dir, "wp_infos_from_ats", wps_fname)
    df = pd.read_csv(file_path)

    # get maximum WP nbr, either from ATADD or from ATS database
    year = df.iloc[0]["meeting_year"]
    if year in max_wp_nbrD:
        max_wp_nbr = max_wp_nbrD[year]
    else:
        max_wp_nbr = max(df["paper_number"])

    # the missing numbers are the set difference between all nbrs
    # in that range and the numbers found
    wp_nbrs = set(df["paper_number"])
    all_nbrs = set(range(1, max_wp_nbr + 1))
    missing = all_nbrs - wp_nbrs

    # if any found missing, make a note of them and 
    if missing:
        missingD[year] = {
            "default_row": dict(df.iloc[0]),
            "missing_wps": sorted(missing),
        }


# write the missing wps to a template CSV
# ---

# years in order
years = sorted(missingD.keys())

# list of dictionaries we'll put in the dataframe
list_of_D_for_df = list()
for year in years:
    default = missingD[year]["default_row"]
    missing_wps = missingD[year]["missing_wps"]
    for wp_number in missing_wps:
        outD = {
            'meeting_year': year,
            'meeting_type': default["meeting_type"],
            'meeting_number': default["meeting_number"],
            'meeting_name': default["meeting_name"],
            'paper_type': default["paper_type"],
            'paper_number': wp_number,
            'paper_revision': None,
            'paper_name': None,
            'agendas': None,
            'parties': None,
            'url': None,
        }
        list_of_D_for_df.append(outD)

# write it to a "template" file
# ---

"""
# get ordered header
file_path = os.path.join(raw_data_dir, "wp_infos_from_ats", wps_fnames[0])
df = pd.read_csv(file_path)
header = sorted(df.columns)
"""

# construct dataframe for ease of writing csv
df = pd.DataFrame.from_records(list_of_D_for_df)

# write
df.to_csv(
    os.path.join(raw_data_dir, "wps_missing_from_ats/wps_missing_template.csv"), 
    index=False
)