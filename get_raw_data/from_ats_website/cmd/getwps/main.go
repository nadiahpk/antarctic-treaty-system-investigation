package main

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"

	// "regexp"
	"strings"
	"time"

	// "unicode"

	"getrawdata/utils"

	api "github.com/carlohamalainen/antarctic-database-go"
)

func getPreferredLanguageLink(documentLinks []api.DocumentLink) (api.DocumentLink, bool) {
	// dictionary from language to DocumentLink
	linkMap := make(map[api.Language]api.DocumentLink)
	for _, link := range documentLinks {
		linkMap[link.Language] = link
	}

	// my preferred-language order
	languageOrder := []api.Language{api.English, api.Spanish, api.French, api.Russian}
	for _, lang := range languageOrder {
		if link, exists := linkMap[lang]; exists {
			return link, true
		}
	}

	// if no language is found, return empty and false
	return api.DocumentLink{}, false
}

func csvMeetingWPs(meeting api.Meeting_Integer) {
	// only search constraint is meeting must be ATCM
	meetingType := api.MeetingType_ATCM_Antarctic_Treaty_Consultative_Meeting
	party := api.Party_All
	paperType := api.PaperType_WP
	category := api.Category_All

	// headers for the CSV
	data := [][]string{
		{
			"meeting_year", "meeting_type", "meeting_number", "meeting_name",
			"paper_type", "paper_number", "paper_revision", "paper_name", "agendas", "parties", "url",
		},
	}

	// get WP info for each WP
	page := 1
	fname := "wp_infos_from_ats/default_name.csv"
	for page > 0 {
		url := api.BuildSearchMeetingDocuments(meetingType, meeting, party, paperType, category, page)

		resp, err := http.Get(url)
		if err != nil {
			panic(err)
		}
		defer resp.Body.Close()

		document := api.Document{}
		if err := json.NewDecoder(resp.Body).Decode(&document); err != nil {
			panic(err)
		}

		for i, item := range document.Payload {
			if i == 0 {
				fname = "wp_infos_from_ats/wps_" + utils.CleanString(fmt.Sprintf("%d", item.Meeting_year)) + ".csv"
			}

			agendaNumbers := []string{}
			for _, agenda := range item.Agendas {
				agendaNumbers = append(agendaNumbers, agenda.Number)
			}
			partyNames := []string{}
			for _, partay := range item.Parties {
				partyNames = append(partyNames, partay.Name)
			}

			documentLinks := api.DownloadLinks(item)
			documentLink, isLink := getPreferredLanguageLink(documentLinks)

			url := ""
			if isLink {
				url = documentLink.Url
			}

			row := []string{
				utils.CleanString(fmt.Sprintf("%d", item.Meeting_year)),
				utils.CleanString(item.Meeting_type),
				utils.CleanString(item.Meeting_number),
				utils.CleanString(item.Meeting_name),
				utils.CleanString(item.Abbreviation),
				utils.CleanString(fmt.Sprintf("%d", item.Number)),
				utils.CleanString(fmt.Sprintf("%d", item.Revision)),
				utils.CleanString(item.Name),
				utils.CleanString(strings.Join(agendaNumbers, " | ")),
				utils.CleanString(strings.Join(partyNames, " | ")),
				url,
			}
			data = append(data, row)

		}

		page = int(document.Pager.Next)
	}

	filepath := filepath.Join(utils.GetRawDataPath(), fname)
	// write csv
	file, err := os.Create(filepath)
	if err != nil {
		log.Fatal("Failed to create file:", err)
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	err = writer.WriteAll(data)
	if err != nil {
		log.Fatal("Failed to write to CSV:", err)
	}

	log.Printf("CSV file created: %s", fname)
}

func main() {
	for i, Meeting_Integer := range api.Meeting_IntegerKeys {
		// https://www.ats.aq/robots.txt asks for 20 seconds between requests
		log.Println("Waiting 20 seconds ... ")
		time.Sleep(20 * time.Second)

		// write a CSV of working papers from this ATCM
		log.Printf("Processing meeting %d", i)
		csvMeetingWPs(Meeting_Integer)
	}
}
