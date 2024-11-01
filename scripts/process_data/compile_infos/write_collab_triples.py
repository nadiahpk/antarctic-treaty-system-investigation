# write the observed collaborations between consultative countries to a CSV

import os
import pandas as pd
import itertools as it
from collections import Counter
import csv
from pathlib import Path

import utils

# -------------------------------------------------------------------

# parameters
# ---

processed_data_dir = Path(os.environ.get("DATA_PROCESSED"))

# get data
# ---

# a list of working papers with more than one consultative country as coauthor
# and which countries they were
df_wps = pd.read_csv(processed_data_dir / "compile_infos/wp_consult_coauthors.csv")


# for each year, count collaborations between consultative-country pairs
# ---

# {year: {"code_1 code 2": count, ...}, ...}
atcm_years = utils.get_atcm_years()
year_2_collabsD = {year: Counter() for year in atcm_years}

for year in atcm_years:
    authorsV = list(df_wps[df_wps["meeting_year"] == year]["consult_countries"])
    for authors in authorsV:
        author_codes = sorted([utils.convert_country_code(author) for author in authors.split(" | ")])
        assert len(author_codes) > 1

        # year_2_collabsD[year].update(it.combinations(author_codes, 2))
        for a, b in it.combinations(author_codes, 2):
            code_pair = " ".join([a, b])
            year_2_collabsD[year][code_pair] += 1

# compress into a string for each year
year_2_collabs = {
    year: " | ".join([
        f"{key} {val}" for key, val in collabsD.items()
    ])
    for year, collabsD in year_2_collabsD.items()
}

# write to file
df = pd.DataFrame([year_2_collabs])
pname = processed_data_dir / "compile_infos/collab_triples.csv"
df.to_csv(pname, index=False, quoting=csv.QUOTE_ALL)