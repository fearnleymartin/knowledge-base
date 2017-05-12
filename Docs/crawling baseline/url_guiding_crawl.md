# Context

Large scale crawl over 5 sites (same as baseline.md) using url guiding.
Let it run over night, using auto throttling.
We set a maximum number of pages at 50 000. However, the crawler may stop earlier if it runs out of links to follow.

Idea is to check how many results we get and what the quality of the results are.

# Crawling statistics

site | number of results pages | number of questions | total number of pages | crawl time (s) | number of errors | questions/page | result/total | pages/sec
https://community.dynamics.com/crm/f/117 | 3836 | 24552 | 4666 | 13044 | 16 (TCP timeout) | 6.4 | 0.82 | 0.35
https://www.reddit.com/r/iphonehelp/ | 1856 | 2215 | 3301 | 4387 | 0 | 1.19 | 0.56 | 0.75 
https://forums.macrumors.com/forums/iphone-tips-help-and-troubleshooting.109 | 
https://community.spiceworks.com/windows?source=navbar-subnav |
https://forum.eset.com/forum/49-general-discussion/ |



# Item quality

To evaluate the item quality we randomly sample 10 items from each data set and measure the following:
- pertinence: is it related to the actual product ?
- question quality: is it a real question/problem ?
- answer quality: does the answer actually answer the question ?
- parsing quality: has the text been correctly parsed ? Are all fields completed ? (1-5)


## Eset



total lines: 24552
line | pertinence | question quality | answer quality | parsing quality | misc
15011 | 1 | 1 | 0 | 3 | Body (almost) and author correctly parsed, date incorrectly parsed. Deleted post for answer so answer not pertinent. Didn't remove date or author from body + there is share text.
21582 | 1 | 1 | 0 | 3 | Same as above + answer is a subsequent post but doesn't answer question (is OP answering himself)
760 | 1 | 1 |1 | 3 | Same as above + OP answering himself (thanks + gives his solution)
1305 | 1 | 1 | 0 | 3 | Is response to question but doesn't answer question
10071 | 1 | 0 | 0 | 3 | Is a forum post but not a question
15127 | 1 | 1 | 1 | 1 | Answers question
13900 | 1  | 1 | 0 | 2 | Mucks up on one author parsing. Is response to question but doesn't answer question
7542 | 1 | 1 | 0 | 3 | Again discussion pertaining to question but not answer to question

Not parsing the correct date. Not removing this date from the body.
Problem with answers not pertinent to the questions.


## Reddit

total lines: 24552
line | pertinence | question quality | answer quality | parsing quality | misc
9 | 0 | 0 | 0 | 3 | Page sort of contains answers, but parser is not extracting all posts: nested problem. Could have been good if page properly parsed.
1376 | 0 | 0 | 0 | 3 | Same as above
224 | 1 | 1 | 0 | 1 | Index pages and the answer is another question
117 | 1 | 1 | 0 | 1 | Same as above
1135 | 1 | 1 | 1 | 5 | worked good
1004 | 1 | 0 | 0 | 5 | Not a question but parsed page well
599 | 0 | 1 | 1 | 1 | 5 | Not on topic but is a good Q|A pair and well parsed
668 | 1 | 1 | 1 | 1 | 5 | worked good

Date, author and body correctly parsed. Not getting all blocks ( nested content)
Also sometimes thinks index pages are results pages, and question previews are questions

Nested: https://www.reddit.com/r/iphonehelp/comments/680o2s/very_strange_ear_piercing_beeping_noise/

## Conclusions

Need to improve parsing of results pages.
Url guiding generally keeps us on topic (most extracts are pertinent)
Questions usually ok, but could have some filtering
Answers tend to suck (forum discussions, and often not answers)