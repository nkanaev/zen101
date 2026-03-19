package main

import (
	"bytes"
	"fmt"
	"html"
	"html/template"
	"log"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/yuin/goldmark"
	"github.com/yuin/goldmark/extension"
)

var languages = []LangEntry{
	{"en", "101 Zen Stories"},
	{"es", "101 Cuentos Zen"},
	{"it", "101 Historia Zen"},
	{"ru", "101 Дзенская История"},
	{"pl", "101 Opowieści Zen"},
}

type LangEntry struct {
	Code string
	Name string
}

type Story struct {
	Title string
	Body  template.HTML
	Num   int
	Href  string
}

type PageData struct {
	Num     int
	Page    string
	Lang    string
	Title   string
	Root    string
	Langs   []LangEntry
	Stories []Story
	Body    template.HTML
	Next    string
}

func main() {
	log.SetFlags(0)
	basedir, err := os.Getwd()
	if err != nil {
		panic(err)
	}

	join := func(parts ...string) string {
		return filepath.Join(append([]string{basedir}, parts...)...)
	}

	glob := func(path string) []string {
		matches, _ := filepath.Glob(path)
		return matches
	}

	md := goldmark.New(
		goldmark.WithExtensions(extension.Typographer),
	)

	tmplData, err := os.ReadFile(join("assets", "base.html"))
	if err != nil {
		panic(err)
	}
	tmpl, err := template.New("base").Parse(string(tmplData))
	if err != nil {
		panic(err)
	}

	h1Re := regexp.MustCompile(`<h1>(.+?)</h1>`)
	doubleNewlineRe := regexp.MustCompile(`\n\n`)

	allStories := map[string][]Story{}
	for _, lang := range languages {
		log.Printf("reading %s stories", lang.Code)
		var stories []Story
		for num := 1; num <= 101; num++ {
			mdPath := join("stories", lang.Code, fmt.Sprintf("%03d.md", num))
			mdBytes, err := os.ReadFile(mdPath)
			if err != nil {
				panic(err)
			}
			var buf bytes.Buffer
			if err := md.Convert(mdBytes, &buf); err != nil {
				panic(err)
			}
			body := doubleNewlineRe.ReplaceAllString(strings.TrimSpace(buf.String()), "\n")

			titleMatch := h1Re.FindStringSubmatch(body)
			if titleMatch == nil {
				panic(fmt.Sprintf("no h1 in %s", mdPath))
			}
			body = strings.TrimSpace(h1Re.ReplaceAllString(body, ""))

			stories = append(stories, Story{
				Title: html.UnescapeString(titleMatch[1]),
				Body:  template.HTML(body),
				Num:   num,
			})
		}
		allStories[lang.Code] = stories
	}

	outdir := join("output")
	if _, err := os.Stat(outdir); err == nil {
		os.RemoveAll(outdir)
	}
	os.MkdirAll(outdir, 0755)

	staticFiles := make([]string, 0)
	staticFiles = append(staticFiles, glob("assets/*.css")...)
	staticFiles = append(staticFiles, glob("assets/*.ico")...)
	staticFiles = append(staticFiles, glob("assets/*.woff")...)
	staticFiles = append(staticFiles, glob("assets/*.woff2")...)
	for _, static := range staticFiles {
		log.Printf("copying %s", static)
		data, err := os.ReadFile(static)
		if err != nil {
			panic(err)
		}
		staticDest := strings.TrimPrefix(static, "assets/")
		if err := os.WriteFile(join("output", staticDest), data, 0644); err != nil {
			panic(err)
		}
	}

	render := func(path string, data PageData) {
		f, err := os.Create(path)
		if err != nil {
			panic(err)
		}
		defer f.Close()
		if err := tmpl.Execute(f, data); err != nil {
			panic(err)
		}
	}

	log.Print("writing index.html")
	render(join("output", "index.html"), PageData{
		Page:  "index",
		Title: "禪",
		Langs: languages,
		Root:  ".",
	})

	for _, lang := range languages {
		log.Printf("writing %s pages", lang.Code)
		stories := allStories[lang.Code]
		os.MkdirAll(join("output", lang.Code), 0755)

		for i, s := range stories {
			num := s.Num
			storyDir := join("output", lang.Code, fmt.Sprintf("%03d", num))
			os.MkdirAll(storyDir, 0755)
			stories[i].Href = fmt.Sprintf("./%03d/", num)

			data := PageData{
				Num:   num,
				Page:  "story",
				Lang:  lang.Code,
				Root:  "../..",
				Title: s.Title,
				Body:  s.Body,
			}
			if num != 101 {
				data.Next = fmt.Sprintf("../%03d", num+1)
			}
			render(filepath.Join(storyDir, "index.html"), data)
		}

		render(join("output", lang.Code, "index.html"), PageData{
			Page:    "toc",
			Lang:    lang.Code,
			Title:   lang.Name,
			Stories: stories,
			Root:    "..",
		})
	}
}
