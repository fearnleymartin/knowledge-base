# knowledge-base
Creating a knowledge base for product orientated discussion

# Run

First time, here? Look at Get Started first.

To activate this environment, use: source activate swisscom
To deactivate this environment, use: source deactivate
If you additional dependencies needed to be installed do not forget to re-export the environment with conda env export > environment.yml.

# Get Started

## Conda

Setup conda environment using environment.yml.

conda env create -f environment.yml


# Solr
Solr config files for the project

To set up the solr configuration : 
- 1) download the solr file : http://lucene.apache.org/solr/ . 
- 2) create a core named ProductDB ( run the command :`bin/solr create -c ProductDB`) . 
- 3) replace the schema.xml and the solr config file by the one in the repo . 
- 4) (not mandatory) if you want to be able to run the test you will need to create a new core CoreTest . 
- 5) start solr on port 8993 `bin/solr start -p 8983` . 

In solr you are in manual mode for the schema   

To perform a query use the solr_query.py . 

# Scrapy

to run crawler:  
`cd knowledge_base`  
`scrapy crawl superuser`

# Json formats

The different json formats are detailed in the directory json_formats.
