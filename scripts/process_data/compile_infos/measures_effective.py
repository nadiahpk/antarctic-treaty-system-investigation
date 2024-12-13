# count the number of measures and the number that went into effect each year

import os
import pandas as pd
from pathlib import Path

import utils as u

# parameters
# ---

raw_data_dir = Path(os.environ.get("DATA_RAW"), ".")
processed_data_dir = Path(os.environ.get("DATA_PROCESSED", "."))
meas_dir = raw_data_dir / "measure_infos_from_ats"

# get Measures info
# ---

if not meas_dir.exists():
    raise FileNotFoundError(f"Directory not found: {meas_dir}. Check your .envrc.")

meas_fnames = [f for f in meas_dir.glob("*.csv")]
list_of_dfs = [pd.read_csv(meas_dir / meas_fname) for meas_fname in meas_fnames]
df_meas = pd.concat(list_of_dfs, ignore_index=True)

# count total number of measures and number Effective for each year
# ---

years = u.get_atcm_years()
countD = {
    year: {
        "nbr_measures": len(df_meas[df_meas["year"] == year]),
        "nbr_not_yet_effective": len(df_meas[(df_meas["year"] == year) & (df_meas["status"] == "Not_yet_effective")]),
        "nbr_did_not_enter_into_effect": len(df_meas[(df_meas["year"] == year) & (df_meas["status"] == "Did_not_enter_into_effect")]),
        "nbr_effective": len(df_meas[(df_meas["year"] == year) & (df_meas["status"] == "Effective")]),
    }
    for year in years
}

# write to CSV
# ---

df_out = pd.DataFrame(countD).T.reset_index()
df_out.columns = ["meeting_year", "nbr_measures", "nbr_not_yet_effective", "nbr_did_not_enter_into_effect", "nbr_effective"]
# df_out["percentage_effective"] = (df_out["nbr_effective"] / df_out["nbr_measures"]) * 100

# Sort the DataFrame by meeting_year
df_out = df_out.sort_values("meeting_year")

# Save the results
output_file = processed_data_dir / "compile_infos/measures_effective.csv"
df_out.to_csv(output_file, index=False)

print(f"Results saved to {output_file}")