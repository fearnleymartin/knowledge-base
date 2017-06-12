# Creating a knowledge base for product-orientated discussion

Code for:
- Extracting content from question-answer sites and forums via a systematic and site-independent approach
- Running a question answering system using Solr, Tensorflow and Neo4j

Find the project report at `Docs/report.pdf`


# Environment

Setup conda environment using environment.yml.
conda env create -f environment.yml

To activate this environment, use: `source activate swisscom`  
To deactivate this environment, use: `source deactivate`  
If additional dependencies needed to be installed do not forget to re-export the environment with `conda env export > environment.yml.`


# Populating the knowledge base (web crawler)

## Scrapy

The crawler is contained in the directory knowledge base. More information on the structure can be found in `docs/scraping.md`

To run crawler (once parameters have been set):  
`cd knowledge_base`  
`scrapy crawl resultsScraper`  

N.B. make sure conda environment is activated.

To set the parameters:  
Open `knowledge_base/knowledge_base/spiders/resultsScraper.py`  
Set `start_urls` to the list of urls you would like the crawler to start crawling from  

To set the url-guiding parameters:  
Open `knowledge_base/knowledge_base/spiders/master.py`  
Set `allow`, `deny` and `restrict_xpaths`. Some examples are given. These parameters allow you to specify which links you would like the crawler to follow. In you leave them empty, the crawler will simply follow all links that remain in the allowed domain.

To get `allow` and `deny` attributes for new sites, navigate to the index page you would like to start crawling at (e.g. a search results page for "iPhone" on your chosen site). Then put in `allow` the url elements common to all index pages pages (e.g. search results pages) and the url elements common to all results pages (e.g. the page where the question and the answers can be found).

To get `restrict_xpath` attribute, again navigate the th eindex page you would like to start crawling at. Then using chrome developer tools, select the links towards results pages. Then take the css class and put the following in `restrict_xpaths`: `gt.css_to_xpath('.<extracted_xpath>')`. Do the same for the pagination links (e.g. links to other pages of the search results).

To set paths:  
Log: in `knowledge_base/knowledge_base/settings.py` set `LOG_FILE`

## scraping settings

In `knowledge_base/knowledge_base/settings.py`:  
- `CLOSESPIDER_PAGECOUNT` : number of pages to crawl before stopping
- `HTTPCACHE_ENABLED` : Enables caching. Saves downloaded pages. Makes recrawling faster, but can take a lot of space
- `DOWNLOAD_DELAY`: allows you to set the download delay between requests to avoid overloading servers
- `AUTOTHROTTLE_ENABLED`: When enabled, overrides DOWNLOAD_DELAY to automatically adjust the delay depending on the server response.

## Using splash

Splash allows you to handle pages where we need to execute javascript. The requests are rerouting via splash if activated.
(https://github.com/scrapy-plugins/scrapy-splash)

To launch:  
`$ docker run -p 8050:8050 scrapinghub/splash`

This must be running to crawl correctly. If you wish to disable it, the the SplashRequests in the spiders must be replaced with Requests.

## Algorithms and tests

The main algorithm behind the crawler is is_results_page. This algorithm detect whether a page containers question/answer pairs and extracts them is so.

The script can be found in `knowledge_base/knowledge_base/scripts/is_results_page.py`  
The evaluation for this test can be found in `knowledge_base/tests/test_is_results_page.py`  
This function will run the algorithm over a set of 180 pages  (`evaluation_set.csv`) and measure the performance. To get more metrics on the performance, run `analyse_results.py` when the test has finished running.

The other script is `is_index_page.py` and the corresponding test `test_is_index_page.py`.

## Google Scraper
This script scrapes the Google search results page for a given query and extracts the list of the first 100 urls.
See `knowledge_base/GoogleScraper/run.py` for usage example.

## FastText filtering solution

Basic FastText implementation which aims to distinguish between answers to questions and general discussion in forums

## Example data

The following data set was extracted from 6 different sites using the url guiding method. 
https://www.dropbox.com/s/xp3z4yfkexkt2d8/swisscom_crawl_data.zip?dl=0

# Querying the database

## Solr
Solr config files for the project

To set up the solr configuration : 
- 1) download the solr file : http://lucene.apache.org/solr/ . 
- 2) create a core named ProductDB ( run the command :`bin/solr create -c ProductDB`) . 
- 3) replace the schema.xml and the solr config file by the one in the repo . 
- 4) (not mandatory) if you want to be able to run the test you will need to create a new core CoreTest . 
- 5) start solr on port 8993 `bin/solr start -p 8983` . 

In solr you are in manual mode for the schema   

To perform a query use the solr_query.py . 



## Demo with Flask api

`python app/query_api`

To open page go to 127.0.0.1:5000/frontend
