package utils

import (
	"regexp"
	"strings"
	"unicode"
)

func CleanString(s string) string {
	s = strings.ReplaceAll(s, "\r", " ")
	s = strings.ReplaceAll(s, "\n", " ")

	// remove control and nonprintable
	re := regexp.MustCompile(`[[:cntrl:]]`)
	s = re.ReplaceAllString(s, "")

	// keep only printable
	s = strings.Map(func(r rune) rune {
		if unicode.IsPrint(r) {
			return r
		}
		return -1
	}, s)

	s = strings.TrimSpace(s)
	re = regexp.MustCompile(`\s+`)
	s = re.ReplaceAllString(s, " ")

	return s
}
