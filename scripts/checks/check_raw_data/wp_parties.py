# find gaps in the wp_infos I have collected from the ATS and ATAAD
# - check changes across revisions, agenda items, parties

import os
import pandas as pd

raw_data_dir = os.environ.get("DATA_RAW")
results_dir = os.environ.get("RESULTS")

# get file names read
# ---

# information about WPs obtained from ATS database
ats_dir = os.path.join(raw_data_dir, "wp_infos_from_ats")
ats_fnames = [f for f in os.listdir(ats_dir) if f.endswith(".csv")]

# information about WPs obtained mainly from ATAAD
ataad_path = os.path.join(raw_data_dir, "wps_missing_from_ats/wps_missing.csv")

# put all ATS database entries into a list
list_of_dfs = [
    pd.read_csv(os.path.join(ats_dir, ats_fname)) for ats_fname in ats_fnames
]

# add the ataad entries
df_ataad = pd.read_csv(ataad_path)
df_ataad = df_ataad[~df_ataad["is_true_gap"]]  # subset to entries w. WP
list_of_dfs.append(
    df_ataad[
        [
            "meeting_year",
            "meeting_type",
            "meeting_number",
            "meeting_name",
            "paper_type",
            "paper_number",
            "paper_revision",
            "paper_name",
            "agendas",
            "parties",
            "url",
        ]
    ]
)

df = pd.concat(list_of_dfs)


# check parties (authors)
# ---

# check for WPs with no parties listed

list_of_parties = set(df["parties"])
assert not any(pd.isnull(df["parties"]))
print("There were no gaps in the authorship entries (parties).\n")

# get the list of all parties ever used

all_partiesV = list()
for parties in list_of_parties:
    partyV = parties.split(" | ")
    all_partiesV += partyV

# reduce to unique
all_partiesS = set(all_partiesV)

print(
    "This is the list of parties that authored WPs in the ATS and ATAAD databases: "
    + ", ".join(all_partiesS)
    + "\n"
)


# instances where party changes between revisions
# ---

# check for WPs with no paper_revision listed

assert not any(pd.isnull(df["paper_revision"]))
print("There were no gaps in the paper_revision entries.\n")
df = df.astype({"paper_revision": int})

# make a note of instances where the authorship changes between revisions

# get year, WP number of each paper with revisions
df_rev = df[df["paper_revision"] > 0]
has_rev = set(
    [
        (meeting_year, paper_number)
        for meeting_year, paper_number in zip(
            df_rev["meeting_year"], df_rev["paper_number"]
        )
    ]
)

# check each WP if parties changed between revisions
parties_changed = list()
for meeting_year, paper_number in has_rev:
    df_subset = df[
        (df["meeting_year"] == meeting_year) & (df["paper_number"] == paper_number)
    ]
    partiesS = set(df_subset["parties"])
    if len(partiesS) > 1:
        parties_changed.append((meeting_year, paper_number))

# if parties changed, write the changes to a file to check later
if parties_changed:
    list_of_dfs = [
        df[(df["meeting_year"] == meeting_year) & (df["paper_number"] == paper_number)]
        for meeting_year, paper_number in sorted(parties_changed)
    ]
    df_out = pd.concat(list_of_dfs)
    path_out = os.path.join(results_dir, "checks/check_raw_data/wp_parties_change_between_revisions_template.csv")
    df_out.to_csv(path_out, index=False)
    print(f"Parties sometimes changed between paper revisions. Info saved in {path_out}\n")
else:
    print("There were no instances where parties changed between paper revisions.\n")
