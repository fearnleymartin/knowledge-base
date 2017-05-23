# Context

Large scale crawl over 5 sites (same as baseline.md) using url guiding.
Let it run over night, using auto throttling.
We set a maximum number of pages at 50 000. However, the crawler may stop earlier if it runs out of links to follow.

Idea is to check how many results we get and what the quality of the results are.

# Crawling statistics

site | number of results pages | number of questions | total number of pages | crawl time (s) | number of errors | questions/page | result/total | pages/sec
https://community.dynamics.com/crm/f/117 | 4700 | 8833 |12123 | 88800 | 64(SSL) + 113 (tcp timeout) | 1.88 | 0.39 | 0.136
https://www.reddit.com/r/iphonehelp/ | 1856 | 2215 | 3301 | 4387 | 0 | 1.19 | 0.56 | 0.75 
https://forums.macrumors.com/forums/iphone-tips-help-and-troubleshooting.109 | 15057 | 68263 | 19738 | 88800 | 303 (SSL) + 221(TCP) | 4.53 | 0.76 | 0.22
https://community.spiceworks.com/windows?source=navbar-subnav | 21646 | 150408 | 29656 | 88800 | 49 (tcp) | 6.94 | 0.73 | 0.33
https://forum.eset.com/forum/49-general-discussion/ | 3836 | 24552 | 4666 | 13044 | 16 (TCP timeout) | 6.4 | 0.82 | 0.35

N.B. for community.dynamics.com, forum.macrumors.com and community.spiceworks.com the logging stopped working after 24h so using what I've got.


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
599 | 0 | 1 | 1 | 5 | Not on topic but is a good Q|A pair and well parsed
668 | 1 | 1 | 1 | 5 | worked good

Date, author and body correctly parsed. Not getting all blocks ( nested content)
Also sometimes thinks index pages are results pages, and question previews are questions

Nested: https://www.reddit.com/r/iphonehelp/comments/680o2s/very_strange_ear_piercing_beeping_noise/

## Spiceworks

total lines: 150408
line | pertinence | question quality | answer quality | parsing quality | misc
---|----
37340 | 1 | 1 | 1 | 2 | Got question title but not question body. Left some extra blabla in title (unfortunately another question)
137324 | 0 | 0 | 0 | 0 | Index page
54967 | 1 | 1 | 1 | 2 | Same as 1st + answer says I agree with above
117 | 1 | 0 | 0 | 1 | Just question title but is not enough. Doesn't get main answer but gets sub answer
52634 | 1 | 1 | 0 | 1 | Doesn't get best answer (see above). Also thinks question body is an answer.
121830 | 1 | 1 | 1 | 4 | Extra stuff in Q title
9510 | 1 | 1 | 0 | 1 | Doesn't get best answer. Also answer is another question.
117322 | 1 | 1 | 0 | 3 | Answer is further discussion but not direct answer

N.B. Updated parsing to incorporate nesting, and so for examples re-ran parsing.

Not getting best answer because of funny nesting. Getting question title but not body because structure is a bit different. Always gets some content which is ok but not necessarily best content on page.

## Dynamics

total lines: 8833
line | pertinence | question quality | answer quality | parsing quality | misc
---|----
4021 | 1 | 1 | 1 | 4 | Cutting body short (only parsing 1st half). Still makes sense though.
2050 | 1 | 1 | 1 | 4 | Body parsing still includes extra info (author, badges etc)
1911 | 1 | 1 | 1 | 4 | Same as above
6049 | 1 | 1 | 1 | 5 | Worked perfect
250 | 1 | 1 | 1 | 1 | Mainly fine but answer body containing some extra stuff
2264 | 1 | 1 | 1 | 5 | Worked good
4898 | 1 | 0 | 1 | 2 | Question is cropped and doesn't make sense. Answer stuff in answer body
4253 | 1 | 1 | 1 | 2 | Kind of OK, but missing some information in questions and same bad parsing of answer body

When parsing, getting duplicates in the answers (i.e. multiple blocks are the same ?)
Block parsing not refined enough. Also question body is often only partial !

## Macrumors

total lines: 68263
line | pertinence | question quality | answer quality | parsing quality | misc
---|----
1056 | 1 | 1 | 1 | 4 | Good but share stuff still included in body
24114 | 1 | 1 | 1 | 4 | same as above
2138 | 1 | 1 | 1 | 4 | saa
13094 | 1 | 1 | 1 | 4 | saa
14876 | 1 | 0 | 0 | 4 | second page of thread so no question and answer means nothing without question
4892 | 1 | 1 | 1 | 4 | saa
23630 | 1 | 0 | 0 | 4 | second page of thread so no question and answer means nothing without question
52519 | 1 | 1 | 0 | 4 | someone asking same question, not an answer

Generally good. Sometimes get second page of thread with no question.
Also posts in thread are not always answers.

## Superuser

Hardcoded crawler

total lines: 14972
line | pertinence | question quality | answer quality | parsing quality | misc
---|----
9668 | 1 | 1 | 1 | 5 | Good
14744 | 1 | 1 | 1 | 5 | Good
3443 | 1 | 1 | 1 | 5 | Good
13080 | 1 | 1 | 1 | 5 | Good
14957 | 1 | 1 | 1 | 5 | Good
12317 | 1 | 1 | 1 | 5 | Good
6479 | 1 | 1 | 1 | 5 | Good
14583 | 1 | 1 | 1 | 5 | Good

## Conclusions

Need to improve parsing of results pages.
Url guiding generally keeps us on topic (most extracts are pertinent)
Questions usually ok, but could have some filtering
Answers tend to suck (forum discussions, and often not answers)

Parsing generally ok, but often doesn't clean enough, or has trouble with funny nesting structures. However always gets a Q/A pair even if not the perfect information that could be extracted from the page.