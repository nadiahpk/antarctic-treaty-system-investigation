# write the observed collaborations between consultative countries 
# over spans to a CSV

import os
import pandas as pd
import itertools as it
from collections import Counter
import csv
from pathlib import Path

import utils as u

# -------------------------------------------------------------------

# parameters
# ---

span_lo = 0
span_hi = 4


# get the collaboration triples each year
# ---

processed_data_dir = Path(os.environ.get("DATA_PROCESSED"))
file_path_collabs = processed_data_dir / "compile_infos/collab_triples.csv"

if not file_path_collabs.exists():
    raise FileNotFoundError(
        f"Data file not found: {file_path_collabs}. Check your .envrc."
    )

year_2_triples = dict(pd.read_csv(file_path_collabs).iloc[0])
year_2_counters = u.convert_year_2_triples_to_year_2_counters(year_2_triples)




# for each span, calculate the triples
# ---

spans_to_create = [span for span in range(span_lo, span_hi + 1)]
years = sorted(year_2_counters.keys())
len_years = len(years)

# get consultative each year
year_2_consult = {
    year: u.get_consult_codes_this_year(year)
    for year in year_2_counters.keys()
}

span_counters = list()
for span_below, span_above in it.product(spans_to_create, repeat=2):

    # sum counters for year-span_below to year+span_above
    y2c_all = {
        years[i]: sum(
            [
                year_2_counters[yrs_to_include]
                for yrs_to_include in years[i - span_below : i + span_above + 1]
            ],
            Counter(),
        )
        for i in range(span_below, len_years - span_above)
    }

    # let the years outside have the same value as the nearest edge
    for i in range(span_below):
        y2c_all[years[i]] = y2c_all[years[span_below]]
    for i in range(len_years - span_above, len_years):
        y2c_all[years[i]] = y2c_all[years[len_years - span_above - 1]]

    # note the above includes ALL coauthorships between countries in 
    # the span, including those that were non-consultative in that year
    # so we need to remove those entries

    y2c = {
        year: {
            (country_1, country_2): value 
            for (country_1, country_2), value in y2c_all[year].items()
            if (country_1 in year_2_consult[year]) and (country_2 in year_2_consult[year])
        }
        for year in years
    }

    # compress into a string for each year
    y2c_str = {
        year: (
            " | ".join([f"{k[0]} {k[1]} {v}" for k, v in y2c[year].items()])
            if year in y2c
            else ""
        )
        for year in years
    }

    # append the span information
    y2c_str.update(
        {
            "source": "data",
            "span_below": span_below,
            "span_above": span_above,
        }
    )
    span_counters.append(y2c_str)

# write to file
# ---

column_order = ["source", "span_below", "span_above"] + years
df = pd.DataFrame(span_counters, columns=column_order)
pname = processed_data_dir / "compile_infos/collab_span_triples.csv"
df.to_csv(pname, index=False, quoting=csv.QUOTE_ALL)
