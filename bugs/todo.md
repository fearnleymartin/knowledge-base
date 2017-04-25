## crawler

- is_results_page: very slow needed optimising
- doesn't work if threads have pagination (i.e. lots of posts)
- process links not yet general
- need to build generalised scraping
- need to build isValidSite
- avoid related results links on results pages
- move all text searches to regex
- improve regex of date parsing for large speed gain: is currently catching a lotof rubbish because just finding number with a seperator and thinks they are dates
- distinguish blog pages and results pages