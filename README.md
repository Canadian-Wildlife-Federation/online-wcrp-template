# Template WCRP
This repository is built and maintained by the Canadian Wildlife Federation (CWF). The repository contains a jupyter book and a Quarto book used for the live reporting of the WCRP.

## Anaconda Prompt
One may want to use a virtual environment with python version 3.8-3.11 installed.
Does not run locally with python version 3.12 or higher

## File structure
In order to change text within the **jupyter book**. only the .md files need to be changed.

For the quarto book, the .qmd files and their text should be updated after pulling the GitHub repo. 

## Quarto Book
To run this locally:

Clone the repo locally

Open watershed-quarto.Rproj in rstudio or IDE of choice

In the console, use renv::restore() to download dependencies

Render book (in build tab of rstudio) to run locally

## Extra info
 - Download quarto for your local machine: https://quarto.org/docs/download/. For more specific information on Quarto please refer to the documentation site: https://quarto.org/docs/guide/. 
 - After choosing your prefered method for rendering the quarto book (i.e., RStudio https://quarto.org/docs/tools/rstudio.html, VS Code https://quarto.org/docs/tools/vscode.html, the command line interface (CLI) of your choosing), clone this GitHub repo and open the folder in the IDE.
 - Because of the python and R code chunks within the qmd files, the environment (in the repo as '_environment') to which the rederer points to when running python code among R code must be updated so that it reflects the Python executable on your local machine (the python.exe file). ![image](https://github.com/Canadian-Wildlife-Federation/Horsefly-WCRP/assets/108288081/8d47e62a-7706-4300-8717-d99b14c2df58)
For the libraries to work properly, it is recommended to install a "virtual environment" in python on your local machine. Find a useful resource for creating a virtual environment in python here: https://docs.python.org/3/library/venv.html.
 - Change the text within the qmd files to reflect the information for the watershed you wish to make an WCRP for. Additionally, change the code in the API calls to reflect the watershed. For example, 'http://159.89.114.239:9002/functions/postgisftw.wcrp_barrier_extent/items.json?watershed_group_code=HORS&barrier_type=' for the Horsefly becomes 'http://159.89.114.239:9002/functions/postgisftw.wcrp_barrier_extent/items.json?watershed_group_code=BULK&barrier_type=' for the Bulkley.
 - In order to reflect new API changes that alter habitat numbers within your watershed, your repo must be first cloned, then the quarto book should be rendered before pushing the changes back to GitHub.
 - In order to change text within the document, look through the .qmd files and find the one you wish to alter. Be careful not to change the "@" labels as they point to specific tables that are cross referenced within the document. See [here](https://www.markdownguide.org/basic-syntax/) for more info on how to make certain syntax changes within .qmd files.


