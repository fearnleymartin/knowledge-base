# Classification problem

165/180

false positives: 5
false negatives: 10
true positives: 74
true negatives: 91
recall: 88%
precision: 94%
accuracy: 92%

## False Positives
https://forums.macrumors.com/forums/iphone-tips-help-and-troubleshooting.109/
This is an index page which is being characterised as a results page, because it contains all the necessary elements.
Problem is that index pages often have the same format, simply they don't have the body text. Here it is confusing body text with title text, thus giving incoherent answers.

https://www.macrumors.com/mac/
Confusing blog post extracts with posts

https://community.spiceworks.com/windows?source=navbar-subnav
Again index page problem

https://support.wix.com/en/ticket/c80d73fd-0599-4b07-a766-440ee5a6c720
??

https://community.mindjet.com/mindjet/topics/reinnstalling_old_version_after_breakdown
None of this site's pages actually work

https://community.mindjet.com/mindjet
index page problem

http://en.community.dell.com/owners-club/
Index page problem

https://community.dynamics.com/crm/f/117/t/229815
??
https://community.dynamics.com/crm/f/117/t/229818
??




## Problems:


# Parsing problem

## Stats

accuracy: 0.5
correctly parsed pages count: 41
total pages: 82


total parsed posts: 479
total posts: 565
percentage of posts parsed: 0.8477876106194691

Only half the pages are correctly parsed, however on  most pages a good part of the posts are parsed if not all of them (85%).
This is often because of the multiple nested tree structure  of posts which means the important higher level posts are parsed, but not all of the replies in the hierarchy.

## Problems

http://stackoverflow.com/questions/42765616/opening-a-3d-scene-in-wpf-using-webbrowser-control
Tags count as a list of  links so post not valid

https://community.mindjet.com/mindjet/topics/determine_size_of_clickable_map_when_exporting_to_the_web,3,0
Date is in a link, which is banned
Also for first post, the elements are in different blocks

https://community.spiceworks.com/topic/1973512-connect-existing-pc-s-to-new-sbs2011-install
Structure isn't handled. Is Q / A // Replies to answer

https://community.dynamics.com/crm/f/117/t/229815
Structure isn't handled .

Often structure is explicitly handled because of multiple nesting. Often however, some of the content is parsed (often the higher level or most important answers). It's quite rare that the parser gets nothing at all. Could also be hand to look at implementing double nesting as it seems to be quite common. I.e. branch for Q and branch for A. The other answers are sub branches  of the main answer (double nesting).

