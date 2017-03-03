## Types of site

two types of site: structured Q/A sites (ex: Stack exchange, Microsoft product support) and unstructured forum discussions (ex MacRumors)

Q/A sites are well covered by proposed json

Unstructured forum discussion less so: forming question answer pairs is not obvious

## Forum discussion ideas

Tagging different reply posts to help identify structure:
- OP (original poster) giving more precision (identified by OP)
- NP (new posters) asking for more precision (identified by NP and question marks)
- answers (identified by NP and no questions)

Problem with forums is it is hard to extract the answer and to know whether question has been properly answered.
In many cases the question is not actually answered or the answers are bad (check the doc, call customer support etc.)
and there are no metrics like on Q/A sites telling us whether an answer is good

## Proposition

We work only with structured Q/A sites. This gives us much higher quality data in general to work with. (Just browsing mac rumor thread should give you an idea of how often it is low quality).

Trade off: we make the work easier and have in general higher quality data, but we have less overall information to work with.

Question: How many different sources are we expecting to work with ?
How many different Q/A sites are there ? Enough ?

## Crawling model

The crawling model is to find index pages and then go through the results.
An index page is defined as a list of links towards other pages. For example most sites have a search function. We search for the product we are working on, for example "Outlook" and this gives us a list of potentials documents to scrape. We thus iterate through the links and scrape the pages returned by the search. N.B. Usually index results are paginated so we also need to be able to go through the different pages.

This model seems so far to be generic enough to generalise to most sites (both Q/A sites and forums sites often work)


## Filtering

We need to be able to identify if a page is relevant for the info we are looking for. Basically we need to detect if it is a problem/solution page about the product we are working on.
Currently we are using tags extracted from the page to do this filtering.
Ideas for generalisation are to use keyword tools (see with Kamil) to extract the keywords from the document and check they match the product in question.

## Scraping

This part is a bit tricky to generalise well. Each site has its unique html structure and unique css class (which we use to extract the right information). Ideas are to define a list of generic css classes to search for.

Currently we have a master crawler, then we define a sub crawler for each site we want to crawl and the parsing is specific to the site. As the project grows, I am hoping to be able to generalise more and more of the parsing.




