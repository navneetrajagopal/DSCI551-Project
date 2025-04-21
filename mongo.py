from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from langchain_openai import ChatOpenAI
from langchain_mongodb.agent_toolkit.database import MongoDBDatabase
from langchain_mongodb.agent_toolkit.toolkit import MongoDBDatabaseToolkit
from langchain_community.agent_toolkits.json.base import create_json_agent
from langchain.agents import initialize_agent, AgentType
from langchain.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import re
from langchain_core.tools import tool
import json
import os
from dotenv import load_dotenv

load_dotenv()
uri = os.getenv("MONGODB_URI")
openai_api_key = os.getenv("OPENAI_API_KEY")
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

enhancement3 = """
You are an assistant that translates natural language requests into MongoDB queries using the MongoDB shell-style syntax only
DO NOT START QUERIES WITH '''mongodb'''

 MANDATORY RULES:
- All queries must start like this: `db.songs.aggregate([...])`, `db.features.aggregate([...])`, or `db.recommendations.aggregate([...])`
- DO NOT return JSON with keys like "db", "collection", "pipeline". This is NOT accepted. 
- DO NOT use JavaScript-style object literals inside JSON.
- Always use double quotes around all field names and string values.
- ONLY use MongoDB shell-style syntax, as if entering into the Mongo shell.
- If the user asks to add or insert data, use the `mongo_insert` tool. Do not generate shell commands. provide Action: mongo_insert
- If the user asks to delete or remove data, use the `mongo_delete` tool. Do not generate shell commands. provide Action: mongo_delete
- If the user asks to update data, use the `mongo_update` tool. Do not generate shell commands. provide Action: mongo_update
- inputs to the insert and delete tool should be strings, do not add json to it

NEVER use shell syntax for insertions or deletions. Always use the appropriate tool.

DO NOT:
- Generate Mongo shell syntax for inserts or deletes; use the tools instead.
- Wrap shell queries in JSON.

DATABASE STRUCTURE:
The database has three collections:
1. `songs` 
2. `features` 
3. `recommendations` 

All collections share the "song_id" field, which should be used for `$lookup` joins.
All collections are also indexed on the "song_id" field.

WHAT YOU CAN DO:
1. Query generation and execution
  - use Action: mongodb_query
   - Use only `aggregate()` for queries.
   - Include stages like `$match`, `$group`, `$lookup`, `$project`, `$sort`, `$limit`, etc.
   - Do not use `find()`. Always use `aggregate()`.
   - for matching, USE REGEX as so: {"Release Date": {"$regex": "^2016"}}))

2. Data modification
   - For adding new documents, use the `mongo_insert` tool. Input must have:
     - `"collection"`: the target collection.
     - `"document"`: the document to insert, which can have:
        - "song": the song name (string).
        - "artists": the artist name(s) (string).
        - "length": the length of the song (string).
        - "album": the album name (string).
        - "release_date": the release date of the song (string in the format YYYY-MM-DD).
        - etc 
     - If no `song_id` is provided, generate one dynamically.
    
   - For removing documents, use the `mongo_delete` tool. Input must contain:
     - `"collection"`: the target collection.
     - `"filter"`: the deletion criteria.
   - NEVER use shell syntax (like `insertOne()` or `deleteMany()`) for these actions.

   - for updating documents use 
3. Schema exploration
   - To list collections, respond with: `db.getCollectionNames()`
   - To see samples: `db.songs.find({}).limit(3)`

DO NOT:
- DO NOT return raw JSON with keys like "db", "collection", or "pipeline"
- DO NOT wrap shell queries in JSON
- DO NOT provide explanations unless explicitly asked
"""


class InsertInput(BaseModel):
    data: str = Field(..., description="A dictionary (or JSON string) with 'collection' and 'document' keys.")


class DeleteInput(BaseModel):
    # collection: str = Field(..., description="The name of the collection")
    # filter: dict = Field(..., description="The filter for deletion")
    data: str = Field(..., description="A dictionary with 'collection' and 'document' keys.")

class UpdateInput(BaseModel):
    data: str = Field(..., description="A dictionary (or JSON string) with 'collection', 'filter', 'update', and optionally 'many' (boolean) keys.")


class MongoInsertTool(BaseTool):
    name: str = "mongo_insert"
    description: str = (
        "This tool inserts a document into a MongoDB collection. "
        "Use this only when the user is adding new data, not when querying or deleting. "
        "The input data can be a dictionary 'collection' and 'document' keys."
    )
    args_schema: Type[BaseModel] = InsertInput

    def _run(self, data: str):
      try:
          # Manually parse the JSON string into a dictionary
          parsed = json.loads(data)
          collection_name = parsed["collection"]
          document = parsed["document"]

          client = MongoClient(uri)
          db = client["music_db"]
          collection = db[collection_name]

          if isinstance(document, list):
              result = collection.insert_many(document)
              return f"{len(result.inserted_ids)} documents inserted with IDs: {result.inserted_ids}"
          else:
              result = collection.insert_one(document)
              return f"Document inserted with ID: {result.inserted_id}"

      except json.JSONDecodeError:
          return "Error: Failed to parse input string into JSON."
      except Exception as e:
          return f"Error inserting document: {e}"

    def _arun(self, data: dict) -> str:
        raise NotImplementedError("This tool does not support async")
  

class MongoDeleteTool(BaseTool):
    name: str = "mongo_delete"
    description: str = (
        "This tool deletes documents from a MongoDB collection based on a filter. "
        "Use this only when the user wants to delete data, not when querying or inserting. "
        "The input data should be a JSON string with the 'collection' and 'filter' keys."
    )
    args_schema: Type[BaseModel] = DeleteInput

    def _run(self, data: str):
        try:
            parsed = json.loads(data)
            collection_name = parsed["collection"]
            filter = parsed["filter"]

            client = MongoClient(uri)
            db = client["music_db"]
            collection = db[collection_name]

            result = collection.delete_many(filter)
            return f"Deleted {result.deleted_count} documents"
        except json.JSONDecodeError:
            return "Error: Failed to parse input string into JSON."
        except Exception as e:
            return f"Error deleting documents: {e}"

    def _arun(self, data: str) -> str:
        raise NotImplementedError("This tool does not support async")


class MongoUpdateTool(BaseTool):
    name: str = "mongo_update"
    description: str = (
        "This tool updates documents in a MongoDB collection based on a filter. "
        "Use this when the user wants to modify existing data. "
        "The input data should be a JSON string with 'collection', 'filter', 'update', and optionally 'many' keys. "
        "Set 'many' to true to update multiple documents."
    )
    args_schema: Type[BaseModel] = UpdateInput

    def _run(self, data: str):
        try:
            parsed = json.loads(data)
            collection_name = parsed["collection"]
            filter_ = parsed["filter"]
            update_ = parsed["update"]
            many = parsed.get("many", False)

            client = MongoClient(uri)
            db = client["music_db"]
            collection = db[collection_name]

            if many:
                result = collection.update_many(filter_, update_)
                return f"Updated {result.modified_count} documents"
            else:
                result = collection.update_one(filter_, update_)
                return f"Updated {result.modified_count} document"

        except json.JSONDecodeError:
            return "Error: Failed to parse input string into JSON."
        except Exception as e:
            return f"Error updating document(s): {e}"

    def _arun(self, data: str) -> str:
        raise NotImplementedError("This tool does not support async")



db = MongoDBDatabase.from_connection_string(
    connection_string=uri,
    database="music_db"
)

# Instantiate LLM
llm = ChatOpenAI(temperature=0, model="gpt-4-turbo", openai_api_key=openai_api_key)

# Create the MongoDB toolkit
toolkit = MongoDBDatabaseToolkit(db=db, llm=llm)

insert_tool = MongoInsertTool()
delete_tool = MongoDeleteTool()
update_tool = MongoUpdateTool()
all_tools = toolkit.get_tools() + [insert_tool, delete_tool, update_tool]
spotify_agent = initialize_agent(
    all_tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
    )

def chat_with_music(): 
    print("\n[Spotify MongoDB] Ask your query or type exit to quit.")

    while True:
        query = input(">>> ")
        if query.lower() == "exit":
            break
        try:
            result = spotify_agent.invoke(enhancement3 + query)
            print(result['output'])
        except Exception as e:
            print(f"Error: {e}")
    