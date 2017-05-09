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
2760 | 1 | 1 | 0 | 3 | Same as above 
11305
10071
15127
13900
7542
5143
14562