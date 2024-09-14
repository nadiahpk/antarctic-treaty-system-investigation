# Raw data

## Decisions made compiling missing WPs

In the few instances where a paper had multiple revisions and I could not find the subsequent revisions,
I assumed that all revisions applied to the same Agenda Items as the first draft.

## Missing data

### Working Paper revisions metadata and pdfs

Of the 309 papers known to have at least 1 revision,
163 of them are missing metadata (i.e., the information in `/data_raw/wp_infos_from_ats`) 
for at least 1 of the revisions (see `/scripts/check/data_raw/wp_parties.py` to perform the count).
The PDFs for these revisions are also unknown / missing.

### Other missing

- 1975, WP 47, only have first page of pdf

## Known quirks

### In ATS database, WPs with non-party author designated as submitted by the Meeting host

The ATS designates all Working Papers with non-party authors (e.g., WPs authored by a Working Group formed during the meeting) 
as being submitted by the host country for that meeting (`/data_raw/wp_infos_from_ats/`).
For example,
ATCM XII (1983) was held in Canberra, Australia,
and the Meeting Agenda and Working Group papers were designated as authored by Australia
(table below).

|nbr  | title | author in ATS | author on front page |
|----:|-------|---------------|----------------------|
| 2   | Twelfth Antarctic Treaty Consultative Meeting Agenda | Australia | None |
| 18  | Draft Recommendation on Man's Impact on the Antarctic Environment | Australia | Environment Working Group |
| 22  | Draft Recommendation on the Collection and Distribution of Antarctic Meteorological Data | Australia | Telecommunications Working Group |
| 23  | Draft Recommendation on Antarctic Telecommunications | Australia | Telecommunications Working Group |
| 25  | Draft Recommendation on Man's Impact on the Antarctic Environment (Code of Conduct) | Australia | Environment Working Group |
| 26  | Draft Recommendation on Operation of the Antarctic Treaty System | Australia | Working Party on Items 10 and 11 |

For WPs I obtained from the ATAAD that did not have a party author,
I followed the convention set by the ATS database above and designated their author
as the host-country of that meeting (`/data_raw/wps_missing_from_ats/`).

### To do

