# Raw data

## Decisions made compiling missing WPs

In the few instances where a paper had multiple revisions and I could not find the subsequent revisions,
I assumed that all revisions applied to the same Agenda Items as the first draft.



## Known quirks

### WPs with non-party author designated as submitted by the Meeting host country

The ATS designates all Working Papers with non-party authors (e.g., WPs authored by a Working Group formed during the meeting) 
as being submitted by the host country for that meeting (`/data_raw/wp_infos_from_ats`).
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

For WPs from the ATAAD that did not have a party author,
I followed the convention set by the ATS database above and designated their author
as the host-country of that meeting (`/data_raw/wps_missing_from_ats`).

### To do

- I don't know of any counter-examples where the agenda item changed between revisions, but I should check that.
- I have seen papers change coauthors between revisions (increase). e.g., 1995 WP 21 increased from Chile to Chile + Norway
- there are missing agenda items from ATS