import numpy as np
import pandas as pd
import os
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter
import pydot

from calc_probability_consensus_2 import (
    calc_probability_consensus as cython_calc_probabililty_consensus,
)

def calc_avg_brier_score(R_b, pars, nbr_measures, nbr_effective, year_2_matD):
    R, b = R_b
    pars["raw_background_influence"] = b
    pars["consensus_threshold_radius"] = R

    assert(len(nbr_measures) == len(nbr_effective) == len(year_2_matD))

    # calculate p_t(R, B, span_lo, span_hi) in vector, one for each year
    prob_passV = [
        cython_calc_probabililty_consensus(pars, matrix.astype(np.float64))
        for year, matrix in year_2_matD.items()
    ]

    # short Brier score for binary events
    avg_brier = np.mean([
        (1 / nbr_tot) * (nbr_hits * (p - 1)**2 + (nbr_tot - nbr_hits) * p**2)
        for p, nbr_hits, nbr_tot in zip(prob_passV, nbr_effective, nbr_measures)
    ])

    return avg_brier


def convert_year_2_triples_to_year_2_counters(
    year_2_collab_triples: Dict[int, str],
) -> Dict[int, Counter]:
    """
    Return a dictionary of Working Paper collaborations between 
    Consultative countries each year.

    Args:
        year_2_collab_triples (Dict[int, str]): Expects format like: 
            {"2020": "US GB 5 | US FR 3"}.
            Keys are years and values are strings of pipe-separated 
            "triples" with the form:
                "code_1 code_2 count_1_2 | code_1 code_3 count_1_3 | ..."
            Each code_i is an ISO 3166-1 two-letter country codes for a
            Consultative country, and count_i_j is the number of Working
            Papers i and j coauthored in year. Only pairs with
            non-zero counts need be included.

    Returns:
        Dict[int, Counter]: year_2_counter: Keys are country codes and
            values are a Counter of how often countries collaborated

    Raises:
        TypeError: If input is not a dictionary
        ValueError: If triples are not in correct format (e.g., "US GB 5")
            or if data cannot be processed for other reasons
    """

    if not isinstance(year_2_collab_triples, dict):
        raise TypeError("Input must be a dictionary")

    try:
        year_2_counters = {
            int(year): Counter(
                {
                    (code_1, code_2): int(count_as_str)
                    for code_1, code_2, count_as_str in [
                        v.split() for v in triples.split(" | ")
                    ]
                }
            )
            for year, triples in year_2_collab_triples.items()
        }
    except ValueError:
        raise ValueError("Invalid format: each triple should be, e.g., 'US GB 5'")
    except Exception as e:
        raise ValueError(f"Failed to process input: {str(e)}")


    return year_2_counters

def get_collaboration_matrices_from_counters(
    year_2_counter: Dict[tuple, int],
) -> Dict[int, np.ndarray]:
    """
    Return a dictionary of Working Paper collaborations between Consultative countries each year.

    Args:
        year_2_counter (Dict[(str, str), int]): Keys are country codes and
            values are a count of how often they collaborated

    Returns:
        Dict[int, np.ndarray]: year_2_mat: Keys are years and values
            are collaboration matrices for the DFJ model. Rows and
            columns are ordered by alphabetical order of country
            codes. Only rows and columns corresponding to countries
            that were Consultative during year are included.

    Raises:
        ValueError: If any input strings do not conform to required
            format.
        FileNotFoundError: If required data files are not found.
    """

    # get years and country codes from auxiliary functions
    # atcm_years = get_atcm_years()
    years = year_2_counter.keys()
    codes = get_ordered_country_codes()

    # create a mapping from country codes to matrix indices
    code_2_idx = {code: idx for idx, code in enumerate(codes)}
    nbr_codes = len(codes)

    # Initialize matrices for all years with zeros. We start with 
    # full matrices and will trim them later
    year_2_fullmatD = {
        year: np.zeros((nbr_codes, nbr_codes), dtype=int) for year in years
    }

    # Parse the input triples and populate the matrices
    for year, counter in year_2_counter.items():
        triples = [(ccodes[0], ccodes[1], count) for ccodes, count in counter.items()]
        try:
            # Vectorise index locations and counts
            idx1s, idx2s, counts = zip(
                *[
                    (code_2_idx[code_1], code_2_idx[code_2], count)
                    for code_1, code_2, count in triples
                ]
            )

            # Update matrix in a vectorised way
            year_2_fullmatD[int(year)][idx1s, idx2s] += counts
            year_2_fullmatD[int(year)][idx2s, idx1s] += counts
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid input format for year {year}: {e}")

    #  determine which countries were consultative for each year
    keep_idxs = {
        year: [code_2_idx[code] for code in get_consult_codes_this_year(year)]
        for year in years
    }
    # trim matrices to include only consultative countries for each year
    year_2_matD = {
        year: fullmat[keep_idxs[year], :][:, keep_idxs[year]]
        for year, fullmat in year_2_fullmatD.items()
    }

    return year_2_matD

def get_collaboration_matrices(
    year_2_collab_triples: Dict[int, str],
) -> Dict[int, np.ndarray]:
    """
    Return a dictionary of Working Paper collaborations between Consultative countries each year.

    Args:
        year_2_collab_triples (Dict[int, str]): Keys are years and
            values are strings of pipe-separated "triples" with the
            form:
                "code_1 code_2 count_1_2 | code_1 code_3 count_1_3 | ..."
            Each code_i is an ISO 3166-1 two-letter country codes for a
            Consultative country, and count_i_j is the number of Working
            Papers i and j coauthored in year. Only pairs with
            non-zero counts need be included.

    Returns:
        Dict[int, np.ndarray]: year_2_mat: Keys are years and values
            are collaboration matrices for the DFJ model. Rows and
            columns are ordered by alphabetical order of country
            codes. Only rows and columns corresponding to countries
            that were Consultative during year are included.

    Raises:
        ValueError: If any input strings do not conform to required
            format.
        FileNotFoundError: If required data files are not found.
    """

    # get years and country codes from auxiliary functions
    atcm_years = get_atcm_years()
    codes = get_ordered_country_codes()

    # create a mapping from country codes to matrix indices
    code_2_idx = {code: idx for idx, code in enumerate(codes)}
    nbr_codes = len(codes)

    # Initialize matrices for all years with zeros. We start with 
    # full matrices and will trim them later
    year_2_fullmatD = {
        year: np.zeros((nbr_codes, nbr_codes), dtype=int) for year in atcm_years
    }

    # Parse the input triples and populate the matrices
    for year, collab_triples in year_2_collab_triples.items():
        triples = [triple.split() for triple in collab_triples.split(" | ")]
        try:
            # Vectorise index locations and counts
            idx1s, idx2s, counts = zip(
                *[
                    (code_2_idx[code_1], code_2_idx[code_2], int(count_as_str))
                    for code_1, code_2, count_as_str in triples
                ]
            )

            # Update matrix in a vectorised way
            year_2_fullmatD[int(year)][idx1s, idx2s] += counts
            year_2_fullmatD[int(year)][idx2s, idx1s] += counts
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid input format for year {year}: {e}")

    #  determine which countries were consultative for each year
    keep_idxs = {
        year: [code_2_idx[code] for code in get_consult_codes_this_year(year)]
        for year in atcm_years
    }
    # trim matrices to include only consultative countries for each year
    year_2_matD = {
        year: fullmat[keep_idxs[year], :][:, keep_idxs[year]]
        for year, fullmat in year_2_fullmatD.items()
    }

    return year_2_matD


def get_consult_codes_this_year(year: int) -> list[str]:
    """
    Return a list of country codes for countries who were Consultative in a given year.

    Args:
        year (int): The year to check for Consultative countries.

    Returns:
        list[str]: consults: Sorted list of ISO 3166-1 two-letter
            country codes for countries that were Consultative in
            the given year.

    Raises:
        ValueError: If the year is not valid.
        FileNotFoundError: If the data file is not found.
    """
    raw_data_dir = Path(os.environ.get("DATA_RAW", "."))
    file_path = raw_data_dir / "year_countries_consultative.csv"

    if not file_path.exists():
        raise ValueError(f"Data file not found: {file_path}. Check your .envrc.")

    df_consults = pd.read_csv(file_path)

    if year < df_consults["year_joined"].min() or year > pd.Timestamp.now().year:
        raise ValueError(f"Invalid year: {year}")

    consults = sorted(
        df_consults[df_consults["year_joined"] <= year]["ISO_code"].unique()
    )

    return consults


def get_atcm_years() -> list[int]:
    """
    Returns a list of all years in which an ATCM was held for which we have data.

    Returns:
        list[int]: atcm_years: Sorted list of ATCM years.

    Raises:
        FileNotFoundError: If the data file is not found.
    """

    raw_data_dir = Path(os.environ.get("DATA_RAW", "."))
    file_path = raw_data_dir / "ATCMs.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}. Check your .envrc.")

    df_atcms = pd.read_csv(file_path)
    atcm_years = sorted(df_atcms["meeting_year"])

    return atcm_years


def get_ordered_country_codes() -> list[str]:
    """
    To make sure our collaboration matrices always have rows and
    columns corresponding to the same consultative countries, we
    will define the ordering alphabetically.

    Returns:
        list[str]: codes: Sorted list of ISO 3166-1 two-letter
            country codes for every Consultative country to the ATS

    Raises:
        FileNotFoundError: If the data file is not found.
    """

    # get the data relating country names to codes
    raw_data_dir = Path(os.environ.get("DATA_RAW", "."))
    file_path = raw_data_dir / "year_countries_consultative.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}. Check your .envrc.")

    df_consults = pd.read_csv(file_path)
    codes = sorted(df_consults["ISO_code"])

    return codes


def convert_country_code(country_input: str) -> str:
    """
    For all countries that are Consultative Parties to the ATS, this
    function converts between the country's name (as used in the ATS
    database) and its ISO 3166-1 two-letter country code. The
    function detects the type of input by the length of the string
    and returns the opposite type.

    Args:
        country_input (str): Can be either the ISO code (2 letters)
            or country name

    Returns:
        str: country_output: Either the ISO code (2 letters) or
            country name, whichever is opposite to the input

    Raises:
        ValueError: If country_input not valid or data file has issue.
    """

    if len(country_input) == 2:
        input_type = "ISO_code"
        output_type = "country"
    else:
        input_type = "country"
        output_type = "ISO_code"

    # get the data relating country names to codes
    raw_data_dir = Path(os.environ.get("DATA_RAW", "."))
    file_path = raw_data_dir / "year_countries_consultative.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}. Check your .envrc.")

    df_consults = pd.read_csv(file_path)
    df_subset = df_consults[df_consults[input_type] == country_input]

    if len(df_subset) != 1:
        raise ValueError(
            f"{country_input} in {file_path} does not have exactly 1 entry"
        )

    country_output = df_subset.iloc[0][output_type]

    return country_output

def get_year_2_matD_given_span(
    year_2_counters: Dict[tuple, int],
    min_year: int,
    max_year: int,
    span_below: int,
    span_above: int,
) -> Dict[int, np.ndarray]:

    years = [y for y in get_atcm_years() if min_year <= y <= max_year]
    len_years = len(years)

    # sum collaborations from year-span_below to year+span_above
    y2c = {
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
        y2c[years[i]] = y2c[years[span_below]]
    for i in range(len_years - span_above, len_years):
        y2c[years[i]] = y2c[years[len_years - span_above - 1]]

    # note that this will also trim the matrix as needed
    # to only those countries consultative in that year
    year_2_matD = get_collaboration_matrices_from_counters(y2c)

    return year_2_matD

def create_dot_file_string(
    consults: List[int],
    edges: Dict[tuple, float],
    edge_opacity: float = 60,
) -> str:

    graph = create_pydot_graph(
        consults,
        edges,
        edge_opacity,
    )
    raw_dot_file = graph.to_string()

    return raw_dot_file

def create_pydot_graph(
    consults: List[int],
    edges: Dict[tuple, float],
    edge_opacity: float = 60,
) -> Any:

    # create a pydot graph

    # initialise and set defaults
    graph = pydot.Dot("my_graph", graph_type="graph")
    graph.set_node_defaults(
        shape="circle",
        fixedsize="true", # make labels a tight fit
        width=0.4
    )
    graph.set_edge_defaults(color=f"#0000FF{opacity_to_hex(edge_opacity)}")

    # add all nodes
    for country in consults:
        graph.add_node(pydot.Node(country, label=country))

    # add all edges
    for (country_1, country_2), weight in edges.items():
        graph.add_edge(pydot.Edge(
            country_1, 
            country_2, 
            len = 1/weight**(1/2), # neato uses len, not weight, for springs
            penwidth = weight,
        ))

    return graph

def opacity_to_hex(
    opacity_percent: float
) -> str:
    """
    Convert opacity percentage (0-100) to hex (00-FF).

    Example usage:

    opacity = opacity_to_hex(70)  # Returns 'B2'
    color_code = f"#0000FF{opacity}"  # Makes '#0000FFB2'
    """
    hex_value = format(int(opacity_percent * 255 / 100), '02X')
    return hex_value
