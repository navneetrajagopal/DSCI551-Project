# DSCI 551 Project

This project is a natural language to SQL and MongoDB query translator utilizing the OpenAI ChatGPT API to translate queries.

## How to use the SQL file  
- First you need to connect a database (we utilized amazon rds but it will be shut down due to incurring costs)
- next you need to use the translator app to import the housing.csv file into the database
- the you will have to edit the SQL.py 
- insert the url for the AWS RDS server
- add your API key into the API key folder
- Then exit


## How to use the Mongo File
- You will need to first add your API key for an LLM into a .env file 
- Along with this key you should also include the database url for the mongodb database
    - This is all setup for our Spotify implementation but it will also be shut down due to incurring costs of dataset size
- Change the LLM type if needed to suit your API key
- exit
- if you would like to accommodate *any* DB, you will need to edit the prompt enhancement, as well as the database name in the custom tools 


## how to use app.py
- run `pip install -r requirements.txt` to get all required libraries
- open the terminal and run python3 app.py
- pick either the spotify or housing dataset
- **ask away!**
