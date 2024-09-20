# Find the consensus threshold radius R* for which 95% of
# negotiations will *start* from a position of consensus

import os
import numpy as np
from scipy.spatial.distance import pdist
import matplotlib.pyplot as plt
from pathlib import Path
import tol_colors as tc
import pandas as pd


# parameters
# ---

opinion_dimensionality = 2
nbr_consultsV = list(range(12, 30))
results_dir = Path(os.environ.get("RESULTS"), ".")
nbr_samples = 10000

# consensus reached if max(distances) <= 2*R:

# find the 95-percentile for every possible nbr Consultative countries in range and store
# ---

ninety_five_percV = [
    np.percentile(
        [
            max(pdist(np.random.randn(nbr_consults, opinion_dimensionality)))
            for sam in range(nbr_samples)
        ],
        95
    )
    for nbr_consults in nbr_consultsV
]

file_path = results_dir / "dfj_model/basics/initial_consensus.csv"
df = pd.DataFrame({"nbr_agents": nbr_consultsV, "max_distance_95_percentile": ninety_five_percV})
df.to_csv(file_path, index=False)

# examples: relationship between max distance and R at extremes
# ---

nbr_consults_to_plot = [nbr_consultsV[0], nbr_consultsV[-1]]

resultsV = list()
for nbr_consults in nbr_consults_to_plot:
    max_distances = list()
    for sam in range(nbr_samples):
        position = np.random.randn(opinion_dimensionality, nbr_consults)
        distances = pdist(position.transpose())  # pairwise euclidean distance
        max_distance = max(distances)
        max_distances.append(max_distance)

    max_distances.sort()
    resultsV.append(
        {
            "max_distances": max_distances,
            "ninety_five_perc": np.percentile(max_distances, 95),
        }
    )


# save figure
# ---

# n is number of categories
n = len(resultsV)
cm = tc.tol_cmap("rainbow_discrete", n)
colourV = [cm(1.0 * i / n) for i in range(n)]

file_path = results_dir / "dfj_model/basics/initial_consensus_examples.pdf"
fig = plt.figure(figsize=(5, 4))
ax = plt.subplot(111)
for nbr_consults, results, colour in zip(nbr_consults_to_plot, resultsV, colourV):
    max_distances = results["max_distances"]
    ax.plot(
        max_distances,
        np.linspace(0, 1, nbr_samples),
        color=colour,
        label=str(nbr_consults),
    )
    ninety_five_perc = results["ninety_five_perc"]
    ax.plot([0, ninety_five_perc], [0.95, 0.95], color=colour, ls="dotted", alpha=0.5)
    ax.plot(
        [ninety_five_perc, ninety_five_perc],
        [0, 0.95],
        color=colour,
        ls="dotted",
        alpha=0.5,
    )

ax.set_xlabel(r"max. Euclidian distance between initial positions", fontsize="large")
ax.set_ylabel(r"cumulative probability", fontsize="large")
ax.set_ylim((0, 1))
ax.set_xlim((1, 7.5))
plt.legend(loc="best", title="nbr. countries")
plt.tight_layout()
plt.savefig(file_path)
plt.close("all")