# Notes to self

## Changes since preliminary model

### Two ways to express coauthorship across revisions

1. Each revision is a separate instnace of authorship/coauthorship
    - will need to guess at the coauthorship of missing revisions
1. Coauthorship is the union across revisions
    - may miss bonus authors from missing revisions

Problem with both is that Working Group papers, which ATS attributes to host country,
are also really coauthored by everyone in that group, though we don't know who that is.

### WPs info

- 1961, recall bad fit of Michael's model, find the WPs that were missing from Parsa and Michael's data included all WPs with coauthorships
    - actually made fit worse to include them (isolated pairs)
- 1992, Michael's data includes n extra "Rules of Procedure" that is an "Other", not a Recommendation
    - Also 1991 includes non-recs
    - There's a bunch you can find in his db by setting RecNumber empty

### To do

- meeting 1961, WP 2 rev 0 is not a WP. Delete
- meeting 1968, WP 42 rev 3 is not really authored by France but by a sub-Working Group. It is almost identical to previous revisions, though, so I guess what we do with this depends on the purpose.
    - change authorship to "Sub-Working Group" or empty if we're interested in coauthorships

- Just went through 1961 by hand, and could find no coauthorship mistakes
- TODO 1962, 2008

1977
    - One issue is there was a Special Prepatory Meeting that isn't quite accounted for in the co-authorships ce1037b8-0905-4894-ac75-805bee3368cb-AU-ATADD-4-BB-AQ-282.pdf
    - WP 10 is by SCAR
    - WP 14 is by UK
    - WP 16, 17 by France
    - WP 19 Rev 1 is in Sp, but could be Argentiana
    - 1977 WP 54 Rev 1, authors are both France and UK according to `list_of_docs_1977.pdf`; also according to pdf
    - WP 68 is by Norway only, not Norway and Bel
    - WP 60 is UK
    - WP 74 is Chile

    - Also, WP 79, 85 shows evidence of input from many countries


## Future analysis

### Examples of non-substantive WPs

- place and date of next meeting
- opening addresses, speeches, other statements by dignitaries
- press release
- list of participants, delegates, agenda items
- list of agenda items
- message of greetings to Antarctic stations
- addendums and errata

Also want to exclude Drafts of the Final Report and Final Reports.

Might also identify by non-substantive Agenda Items.

### OCR

- situations:
    - Up to ATCM 19 (1995) inclusive, the pdfs have no layer of text, need LLM OCR 
    - From ATCM 20-22 (1996-1998) inclusive, the pdfs have a layer of text, and it's passable but not perfect quality
    - From ATCM 23 (1997) onwards inclusive, the pdfs have a high-quality layer of text under them, and OCR should be fairly straightforward.
- 2498 WPs total, with 1092 up to and incl. 1996
- For the final reports, ATCM27_fr001_e.pdf doesn't have embedded text, and ATCM28_fr001_e.pdf does
- could use spelling mistakes per word to compare how text quality degenerates back in time

### Links available in Final Reports

#### Summary

- Meetings up to and incl. 5 (1963) don't have standard-looking minutes.
    - Probably going to have to do these by hand
- After about Meeting 7 (1972), the minutes are detailed enough to start to see connections
- Will need to do a tracking of how Agenda changes from before to after Meeting
- Some early meetings have Agenda -> Rec but for previous meetings' Recs. Understand.
- Need to do a few case studies of how to track through years

#### Details up to Meeting 10

- Meeting 1 has the full text of recommendations inserted into the minutes.
    - Minutes restart at page 12.
    - It's not organised by Agenda Item.
- Meeting 2 (1962) has basically no minutes of the discussion.
    - The only useful thing might be the Agenda and Working Groups.
- Meeting 3 (1964) also don't have useful minutes, though the WPs seem to tell a story.
    - Let's look at ATCM 1, Protection of fauna and flora.  There's redrafting of Art IV mentioned, and X and XI.  Those Arts appear under III-VIII.  It could be that the WPs under this AI might tell the story...
- Meeting 4 (1966) has nothing by way of minutes, basically.
    - I wonder if some of it is missing. Check ATAAD
    - BUT very usefully it has a list of Agenda -> Rec relationships for Recs from the previous meeting
- Meeting 5 has 9 paragraphs, the first 5 are procedural (e.g., opening statements), 6 lists the agenda, 8 and 9 are procedural.  
    - Paragraph 7 is the only paragraph dealing with the substantive agenda items, and it simply says that the meeting considered all Agenda items in plenary session, and appointed Working Groups for select Items.  
    - Then it lists the Recommendations and some Annexes.
- Meeting 6 (1970), sixteen paragraphs long, has a little more details about decision-making.
    - For example, par. 10 explains why Item 5 about the conservation of seals was considered outside their scope, and mentions the drafting of a new convention on seals that would be circulated as a WP
    - At the end, a list of Documents of the meeting
- Meeting 7 (1972) has 33 paragraphs divided by agenda item, and is usefully starting to look like minutes of deliberations.
    - We see par. 9 discussing seals killed and whether there's a risk of over-exploitation,
    - and par. 29 about a special conference about seals, which Chile wanted brought back into the ATS scope.
- Meeting 8 (1975) notes changes to the agenda; 
    - very usefully, the minutes paragraphs are split by agenda item.
        - (So we need to track the agenda items changes from before to after the meeting)
    - List of docs at the end.
Meeting 9 (1977),
    - has Agenda -> Rec relationships for Recs from the previous meeting. I need to study one of these.
- Meeting 10 (1979) has a pretty detailed minutes for each working group. 
    - It links the work to previous years' recommendations. For example, par. 13 says the Workign Group on oil considered Rec IX-6,
the Report of the Group of Eco and other experts (Annex 6), and some other materials.


## Misc to-do
