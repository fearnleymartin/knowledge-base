Site to crawl (500 pages):
No product filter
Simply looking for results pages
Comparing no url guiding with url guiding
Looking at ratios of results pages obtained
And time
This is supposing isResultsPage works correctly
Also remember we don't consider pages to be results pages if the question hasn't been answered

# Site 1
https://community.dynamics.com/crm/f/117
## Baseline
results: 9, total: 514, ratio: 0.0175097276265
Seems to have worked correctly
## URL guiding
results: 223, total: 510, ratio: 0.437254901961

# Site 2
https://www.reddit.com/r/iphonehelp/
## Baseline
results: 394, total: 511, ratio: 0.771037181996
Seems good but basically completely mucked up because is not correctly identifying the results pages
## URL guiding
results: 305, total: 514, ratio: 0.593385214008

# Site 3
https://forums.macrumors.com/forums/iphone-tips-help-and-troubleshooting.109
## Baseline
results: 11, total: 507, ratio: 0.0216962524655
Got stuck in a loop of redirect, and going to lots of useless urls
## URL guiding
results: 398, total: 514, ratio: 0.774319066148

# Site 4
https://community.spiceworks.com/windows?source=navbar-subnav
## Baseline
results: 143, total: 496, ratio: 0.288306451613
Seems good but in reality, is overestimating the number of results pages because is classifying pages as results pages which actually are not
## URL guiding
results: 297, total: 514, ratio: 0.577821011673

# Site 5
https://forum.eset.com/forum/49-general-discussion/
## Baseline
results: 37, total: 510, ratio: 0.0725490196078
Seems to have worked correctly
## URL guiding
results: 385, total: 514, ratio: 0.749027237354

# Conclusion:
Much more efficient with url guiding. Doesn't take much to implement url guiding, but is not 100% automatic.