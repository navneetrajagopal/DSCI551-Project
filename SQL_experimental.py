import os
from sqlalchemy import create_engine, text
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import Dict, Any, Type
from langchain_core.tools import BaseTool
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents import initialize_agent, AgentType
import warnings

warnings.filterwarnings("ignore")


# === Setup ===
os.environ['OPENAI_API_KEY'] = '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'
openai_api_key = os.getenv('OPENAI_API_KEY')

database_uri = "mysql+pymysql://admin:Dsci-551@database-1.cjc8aikg8tmh.us-east-2.rds.amazonaws.com/DSCI551"
engine = create_engine(database_uri)
database = SQLDatabase(engine)

llm = ChatOpenAI(model="gpt-4", temperature=0, openai_api_key=openai_api_key)

# === Input Schemas ===
class SQLInsertInput(BaseModel):
    table: str
    values: Any  

class SQLUpdateInput(BaseModel):
    table: str
    values: Any
    where: Any 
class SQLDeleteInput(BaseModel):
    table: str
    where: Any  

class SQLQueryInput(BaseModel):
    query: str


# === SQL Tools ===
class SQLInsertTool(BaseTool):
    name: str = "sql_insert"
    description: str = "Inserts a row into a SQL table. Only supports single-row insert."
    args_schema: Type[SQLInsertInput] = SQLInsertInput

    def _run(self, table: str, values: Dict[str, Any]) -> str:
        if "UniqueID" not in values:
            return "ERROR: INSERT must include a UniqueID."

        try:
            with database._engine.begin() as conn:
                check = conn.execute(
                    text(f"SELECT COUNT(*) FROM {table} WHERE UniqueID = :id"),
                    {"id": values["UniqueID"]}
                )
                if check.scalar() > 0:
                    return f"ERROR: UniqueID {values['UniqueID']} already exists in {table}."

                columns = ', '.join(values.keys())
                placeholders = ', '.join([f":{k}" for k in values])
                conn.execute(
                    text(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"),
                    values
                )
            return f" Inserted into {table}: {values}"
        except Exception as e:
            return f"Error during insert: {e}"

class SQLUpdateTool(BaseTool):
    name: str = "sql_update"
    description: str = "Updates a single row in a SQL table based on WHERE condition."
    args_schema: Type[SQLUpdateInput] = SQLUpdateInput

    def _run(self, table: str, values: Dict[str, Any], where: Dict[str, Any]) -> str:
        try:
            set_clause = ', '.join([f"{k} = :val_{k}" for k in values])
            where_clause = ' AND '.join([f"{k} = :w_{k}" for k in where])
            params = {f"val_{k}": v for k, v in values.items()}
            params.update({f"w_{k}": v for k, v in where.items()})

            with database._engine.begin() as conn:
                result = conn.execute(
                    text(f"UPDATE {table} SET {set_clause} WHERE {where_clause}"),
                    params
                )
            return f"SUCCESS: Updated {result.rowcount} row(s) in {table}"
        except Exception as e:
            return f"Error during update: {e}"

class SQLDeleteTool(BaseTool):
    name: str = "sql_delete"
    description: str = "Deletes a single row from a SQL table based on WHERE condition."
    args_schema: Type[SQLDeleteInput] = SQLDeleteInput

    def _run(self, table: str, where: Dict[str, Any]) -> str:
        try:
            where_clause = ' AND '.join([f"{k} = :{k}" for k in where])
            with database._engine.begin() as conn:
                result = conn.execute(
                    text(f"DELETE FROM {table} WHERE {where_clause}"),
                    where
                )
            return f"Deleted Deleted {result.rowcount} row(s) from {table}"
        except Exception as e:
            return f"Error during delete: {e}"
        
class SQLQueryTool(BaseTool):
    name: str = "sql_query"
    description: str = "Executes a raw SQL query for read-only access like SELECT, SHOW TABLES, SHOW COLUMNS."
    args_schema: Type[SQLQueryInput] = SQLQueryInput

    def _run(self, query: str) -> str:
        try:
            with database._engine.begin() as conn:
                result = conn.execute(text(query))
                return str([dict(zip(result.keys(), row)) for row in result])
        except Exception as e:
            return f"Error during query: {e}"



# === Register Tools ===
sql_tools = [
    SQLInsertTool(),
    SQLUpdateTool(),
    SQLDeleteTool(),
    SQLQueryTool()
]

# === Agent Setup ===
from langchain.agents import AgentExecutor




insert_tool = SQLInsertTool()
delete_tool = SQLDeleteTool()
update_tool = SQLUpdateTool()
sql_query_tool = SQLQueryTool()

all_tools = sql_tools + [insert_tool, delete_tool, update_tool, sql_query_tool]


agent = initialize_agent(
    all_tools,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    handle_parsing_errors=True
)

# === Query Function ===
def query_housing_database(question: str):
    try:
        enhancement = '''
- All tables share the key UniqueID.
- Always use JOINs on UniqueID when combining tables.
- Use only these valid table names: OWNER_DETAIL, PROPERTY_INFO, SALE_TRANSACTIONS.
- Do not use variations like OWNER_DETAILS or PROPERTY_INFOS.
- Do not use ACREAGE unless specifically mentioned.
- Only perform ONE insert or delete per query.
- Use SELECT to check if UniqueID exists before insert.
- If UniqueID exists, do not insert or delete.
- Use only a single WHERE clause for DELETE or UPDATE.
- Quote all string and VARCHAR values.
- Do not explain the SQL output.
- Avoid multiline or bulk insert/delete logic.
- Assume HOUSE = PROPERTY in context.
- Do not use PROPERTY_INFO.TotalValue
- run SHOW TABLES when asked tabout the tables (ex: what are all the tables, what are the tables, what tables exit, show existing tables, show me the tables, show me all the tables, list the tables, list all the table)
- run SHOW COLUMNS from table_name when asked about the columns and names (ex: what are the column names in the tables, what  are all the col names, col names, column names, what are all the columns in table, what are the columnsin table, what columns exit in table, show existing columns in table, show me the columns in table, show me all the columns in table, list the columns in table, list all the columns in table)
- ex: run show columns from property_info when asked about columns in property info
'''

        final_prompt = enhancement.strip() + "\n" + question.strip()

        result = agent.invoke({"input": final_prompt}, return_only_outputs=True)
        print("\n Final Answer:\n", result["output"])
        return result["output"]
    except Exception as e:
        print(f"\n Error: {e}")
        return None
### add to the app.py
def experimental_queries():
    print("Welcome to the Experimental Housing Query CLI. This has not been fully tested compared to the other model. Type 'exit' to return to the main menu.\n")

    while True:
        user_prompt = input("Enter your query: ").strip()
        if user_prompt.lower() == "exit":
            print("Exiting housing query interface.\n")
            break

        try:
            result = query_housing_database(user_prompt)
            if result:
                print("\nQuery Result:\n", result)
        except Exception as e:
            print(f"\nError: {e}\n")

# To run interactively
if __name__ == "__main__":
    experimental_queries()
