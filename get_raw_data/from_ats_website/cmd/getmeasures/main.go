package main

import (
	"encoding/csv"
	"encoding/json"
	"fmt"

	"log/slog"
	"net/http"
	"os"

	"regexp"
	"strings"
	"time"

	"getrawdata/utils"
	"path/filepath"

	api "github.com/carlohamalainen/antarctic-database-go"
)

type MyMeasure struct {
	Measure     api.Measure
	URL         string
	Status      string
	DocType     string
	IRecNo      string
	MeetingName string
	MeetingYear string
}

func cleanAndJoinCategorys(input string) string {
	// split the input into lines for windows, linux, mac
	re := regexp.MustCompile(`\r\n|\n|\r`)
	lines := re.Split(input, -1)

	var items []string
	for _, line := range lines {
		// Clean the line
		item := utils.CleanString(line)

		// If the item is not empty, add it to the list
		if item != "" {
			items = append(items, item)
		}
	}

	// Join the items with "|"
	return strings.Join(items, " | ")
}

func cleanAndJoinTopics(input string) string {
	// Split the input into lines
	lines := strings.Split(input, "\n")

	var items []string
	for _, line := range lines {
		// Trim whitespace and remove leading "-"
		item := strings.TrimSpace(line)
		item = strings.TrimPrefix(item, "-")
		item = strings.TrimSpace(item)

		// If the item is not empty, add it to the list
		if item != "" {
			items = append(items, item)
		}
	}

	// Join the items with "|"
	return strings.Join(items, " | ")
}

func docTypeToString(docType api.DocType) string {
	switch docType {
	case api.DocType_CEP:
		return "CEP"
	case api.DocType_Decision:
		return "Decision"
	case api.DocType_Measure:
		return "Measure"
	case api.DocType_Other:
		return "Other"
	case api.DocType_Recommendation:
		return "Recommendation"
	case api.DocType_Resolution:
		return "Resolution"
	case api.DocType_Treaty:
		return "Treaty"
	default:
		panic("internal error")
	}
}

func statusToString(status api.Status) string {
	switch status {
	case api.Status_Did_not_enter_into_effect:
		return "Did_not_enter_into_effect"
	case api.Status_Effective:
		return "Effective"
	case api.Status_Not_yet_effective:
		return "Not_yet_effective"
	default:
		panic("internal error")
	}
}

func getThisYearsMeasures(meeting api.Meeting_Date) []MyMeasure {
	// search all categories and topics
	cat := api.Cat_All
	topic := api.Topic_All

	myMeasures := []MyMeasure{}

	for _, status := range api.StatusKeys {

		// for Recommendations and for Measures
		for _, docType := range []api.DocType{api.DocType_Recommendation, api.DocType_Measure} {

			// for each page
			page := 1
			for page > 0 {
				url := api.BuildSearchURL(meeting, cat, topic, docType, status, page)

				resp, err := http.Get(url)
				if err != nil {
					panic(err)
				}
				defer resp.Body.Close()

				document := api.Treaty{} // has Pager and Payload
				if err := json.NewDecoder(resp.Body).Decode(&document); err != nil {
					panic(err)
				}

				// for each Rec/Meas in the payload
				// get its data from the second URL and store
				for _, payLoad := range document.Payload {
					myMeasure := MyMeasure{}

					myMeasure.DocType = docTypeToString(docType)
					myMeasure.Status = statusToString(status)

					myMeasure.IRecNo = payLoad.Irecno
					myMeasure.MeetingName = payLoad.Satcmno
					myMeasure.MeetingYear = fmt.Sprintf("%d", payLoad.Yearmeeting)

					url2 := api.BuildSecondURL(meeting, cat, topic, docType, status, payLoad.Arecid)
					myMeasure.URL = url2

					resp, err = http.Get(url2)
					if err != nil {
						panic(err)
					}
					defer resp.Body.Close()

					if resp.StatusCode != 200 {
						panic(fmt.Sprintf("bad response code %d on %s", resp.StatusCode, url2))
					}

					measure := api.ParseMeasure(url2, resp.Body)
					myMeasure.Measure = measure

					myMeasures = append(myMeasures, myMeasure)
				}

				page = document.Pager.Next

			} // for each page

		} // for Recommendations and Measures

	} // for each status

	return myMeasures
}

/*
func assertNoUnknownKeys(myMeasure MyMeasure, m map[string]string, knownKeys []string) {
	if !haveSameKeys(m, knownKeys) {
		slog.Warn("map keys do not match expected keys",
			"expected", fmt.Sprintf("%+v", knownKeys),
			"got", fmt.Sprintf("%+v", getKeys(m)),
			"url", myMeasure.URL,
		)
	}
}
*/

func noUnknownKeys(myMeasure MyMeasure, m map[string]string, knownKeys []string) {
	knownKeysMap := make(map[string]bool)
	for _, key := range knownKeys {
		knownKeysMap[key] = true
	}

	for key := range m {
		if !knownKeysMap[key] {
			slog.Warn("map keys not found in known keys",
				"key", key,
				"url", myMeasure.URL,
			)
		}
	}

}

/*
func haveSameKeys(m map[string]string, keys []string) bool {
	if len(m) != len(keys) {
		return false
	}
	for _, key := range keys {
		if _, exists := m[key]; !exists {
			return false
		}
	}
	return true
}

func getKeys(m map[string]string) []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	return keys
}
*/

func csvMeasures(myMeasures []MyMeasure) {
	// file name for the CSV
	year := utils.CleanString(myMeasures[0].MeetingYear)
	fname := fmt.Sprintf("measure_infos_from_ats/measures_%s.csv", year)

	// headers for the CSV
	data := [][]string{
		{
			"number",
			"measure_type",
			"title",
			"subject",
			"year",
			"meeting_name",
			"status",
			"status_details",
			"category",
			"topics",
			"attachments",
			"final_report_par",
			"memo",
			"approvals",
			"approvals_text",
			"url",
			"text_file",
		},
	}

	// write a data row for each measure
	for _, myMeasure := range myMeasures {
		measure := myMeasure.Measure

		// the characteristics should be:
		// Subject, Status, Category, Topics, Attachments, Relevant Final Report paragraph
		// Sometimes we get Memo (e.g., https://www.ats.aq/devAS/Meetings/Measure/104?s=1&iframe=1&from=06/20/1975&to=06/20/1975&cat=0&top=0&type=1&stat=4&txt=&curr=0)
		charMap := make(map[string]string)
		for _, char := range measure.Characteristics {
			title := char.Title
			text := char.Text
			if char.Url != nil {
				text = fmt.Sprintf("%s | %s", text, *char.Url)
			}
			charMap[title] = text
		}
		knownKeys := []string{
			"Subject",
			"Status",
			"Category",
			"Topics",
			"Attachments",
			"Relevant Final Report paragraph",
			"Memo",
		}
		noUnknownKeys(myMeasure, charMap, knownKeys)

		// []Approval, type Approval struct {Date    string Country string}
		var approvals []string
		for _, approval := range measure.Approvals {
			item := fmt.Sprintf("%s | %s", approval.Date, approval.Country)
			approvals = append(approvals, item)
		}
		approvalsString := strings.Join(approvals, " || ")

		// write a row
		docType := utils.CleanString(myMeasure.DocType)
		iRecNo := utils.CleanString(myMeasure.IRecNo)

		getWithDefault := func(m map[string]string, key string, clean func(string) string) string {
			value, ok := m[key]
			if ok {
				return clean(value)
			}
			return ""
		}

		row := []string{
			iRecNo,
			docType,
			utils.CleanString(measure.Title),
			getWithDefault(charMap, "Subject", utils.CleanString),
			year,
			utils.CleanString(myMeasure.MeetingName),
			utils.CleanString(myMeasure.Status),
			getWithDefault(charMap, "Status", utils.CleanString),
			getWithDefault(charMap, "Category", cleanAndJoinCategorys),
			getWithDefault(charMap, "Topics", cleanAndJoinTopics),
			getWithDefault(charMap, "Attachments", utils.CleanString),
			getWithDefault(charMap, "Relevant Final Report paragraph", utils.CleanString),
			getWithDefault(charMap, "Memo", utils.CleanString),
			utils.CleanString(approvalsString),
			utils.CleanString(*measure.ApprovalText),
			utils.CleanString(myMeasure.URL),
			fmt.Sprintf("data_raw/measure_texts_from_ats/%s/%s_%s.txt", year, docType, iRecNo),
		}

		data = append(data, row)
	}

	// write csv
	file, err := os.Create(filepath.Join(utils.GetRawDataPath(), fname))
	if err != nil {
		panic(err)
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	err = writer.WriteAll(data)
	if err != nil {
		panic(err)
	}

	slog.Info("wrote CSV file", "filename", fname)
	// log.Printf("CSV file created: %s", fname)

}

func txtMeasures(myMeasures []MyMeasure) {

	// write a TXT file each measure
	for _, myMeasure := range myMeasures {

		measure := myMeasure.Measure

		// file name for the TXT file
		year := myMeasure.MeetingYear
		docType := myMeasure.DocType
		nbr := myMeasure.IRecNo
		fname := filepath.Join(
			utils.GetRawDataPath(),
			fmt.Sprintf("measure_texts_from_ats/%s/%s_%s.txt", year, docType, nbr),
		)

		// content for the file
		content := measure.Title + "\n\n" + measure.Content

		// write the directory and TXT file
		dir := filepath.Dir(fname)
		err := os.MkdirAll(dir, 0755) // rwxr-xr-x
		if err != nil {
			panic(err)
		}

		err = os.WriteFile(fname, []byte(content), 0644) // rw-r--r--
		if err != nil {
			panic(err)
		}

		slog.Info("wrote measures", "filename", fname)
	}
}

func main() {
	logger := slog.New(slog.NewTextHandler(os.Stdout, nil))
	slog.SetDefault(logger)

	for i, meeting := range api.Meeting_DateKeys {
		if strings.Contains(api.Meeting_DateToString(meeting), "_ATCM_") {
			// https://www.ats.aq/robots.txt asks for 20 seconds between requests
			slog.Info("waiting 20 seconds")
			time.Sleep(20 * time.Second)
			slog.Info("processing meeting", "index", i, "meeting_name", api.Meeting_DateToString(meeting))

			// write CSV and TXT files for each measure in this year
			myMeasures := getThisYearsMeasures(meeting)
			if len(myMeasures) == 0 {
				slog.Info("no measures found", "meeting", api.Meeting_DateToString(meeting))
				continue
			}
			csvMeasures(myMeasures)
			txtMeasures(myMeasures)
		}

	}
}
