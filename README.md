# DSCI 551 Project

This project is a natural language to SQL and MongoDB query translator utilizing the OpenAI ChatGPT API to translate queries.

The SQL.py file is the file that executes the SQL queries using LangChain + OpenAI's ChatGPT translating natural language against a MySQL database. This file utilizes a custom langchain prompt with a strict template that allows the LLM to generate accurate and valid SQL Queries. The queries are translated via LangChain's LLMChain and then run using SQLAlchemy, before being output at the standard SQL output.

The mongo.py script defines a natural language interface to a MongoDB database utilizing LangChain and OpenAI ChatGPT to perform aggregate, insert/update/delete, and schema inspection. This script gives a strict prompt to keep the LLM operating within the set guidelines of aggregate, and defines its own set of tools for insert, delete, and update. These tools allow for safe callable functions to insert one or many documents, delete one or many documents, and update one or many documents. This agent utilizes an agent style to handle query execution and errors, while taking natural user input and running it against the agent.



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


## how to use app.py
- run `pip install -r requirements.txt` to get all required libraries
- open the terminal and run python3 app.py
- pick either the spotify or housing dataset
- **ask away!**
