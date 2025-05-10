# DSCI 551 Project

This project is a natural language to SQL and MongoDB query translator utilizing the OpenAI ChatGPT API to translate queries.

The SQL.py file is the file that executes the SQL queries using LangChain + OpenAI's ChatGPT translating natural lanaguage against a MySQL database. This file utlizies a custom langchain prompt with a strict template that allows the LLM to generate accurate and valid SQL Queries. The queries are translated via LangChain's LLMChain and then run using SQLAlchemy, before being output at the standard SQL output.

The mongo.py script defines a natural language interface to a MongoDB database utilizing LangChain and OpenAI CHATGPT to perform aggregate, insert/update/delete, and schema inspection. This script gives a strict prompt to keep the LLM operating within the set guidlines of aggregate, and defines its own set of tools for inser, delete, and update. These tools allow for safe callable functions to insert one or many documents, delete one or many documents, and update one or many documents. This agent utilizes a agent style to handle query execution and errors, while taking natural user input and running it against the agent.

Finally, the experimental SQL file was created as a suggestion from our TA as a possible future interaction. The TA liked the agent based interaction of mongo.py and implied a future possibility with the SQL. We chose to make an attempt just to show the possibilities of the agents and the tools we had created. It is a juxtaposition of the SQL and Mongo files from earlier. Where we created custom tools for insert, update, delete, and general queries while utilizing a similar agent. 

## How to use the SQL file  
- First you need to connect a database (we utilized amazon rds but it will be shut down due to incurring costs)
- next you need to use the csv2rds.py to import the housing.csv file into the database
- the you will have to edit the SQL.py 
- insert the url for the AWS RDS server
- add your API key into the API key folder
- Then exit


## How to use the Mongo File
- You will need to first add your API key for an LLM into a .env file 
- Along with this key you should also include the database url for the mongodb database
    - This is all setup for our mongoDB setup but it will also be shut down like our rds
- Change the LLM type if needed to suit your API key
- exit
- if you would like to accommodate *any* DB, you will need to edit the prompt enhancement, as well as the database name in the custom tools 


## How to use the experimental file
### this is an experimental file, the results have been verified but not to the extent as the sql above. There can be issues this exists as a suggestion from the TA as an alternate procedure and is strictly to show another implementation.
- First you need to connect a database (we utilized amazon rds but it will be shut down due to incurring costs)
- next you need to use the csv2rds.py to import the housing.csv file into the database
- the you will have to edit the SQL.py 
- insert the url for the AWS RDS server
- add your API key into the API key folder
- Then exit

## how to use app.py
- run `pip install -r requirements.txt` to get all required libraries
- open the terminal and run python3 app.py
- pick either the spotify or housing dataset
- **ask away!**
