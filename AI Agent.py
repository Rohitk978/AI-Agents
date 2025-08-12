import os 
from typing import Annotated,TypedDict,List,Literal
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage,HumanMessage,SystemMessage,AIMessage
from langgraph.graph import StateGraph,START,END
from langgraph.prebuilt import create_react_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode


from dotenv import load_dotenv
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Define the state.
class Agentstate(MessagesState):
    next_agent:str       
    # which agent should go next.
    
# Create tools.
@tool 
def search_web(query:str)->str:
    """searchh the web for information"""
    search = TavilySearchResults(max_results=3)
    results = search.invoke(query)
    return str(results)

@tool
def write_summary(content:str)->str:
    """write a summary of provided content"""
    # Simple summary generation.
    summary = f"Summary of findings: \n \n {content[:500]}..."
    return summary

from langchain.chat_models import init_chat_model
llm = init_chat_model("groq:llama-3.1-8b-instant")

# Define agent function.
def researcher_agent(state:Agentstate):
    """researcher agent that seaches for information"""
    messages = state["messages"]
    # Add system message for context
    system_msg = SystemMessage(content="You are the research assistant. Use the web to search the relevant information.")
    # Call llm with tools
    researcher_llm = llm.bind_tools([search_web])
    # Now it store the outptut in messages and show the output with system_msg & messages together.
    response = researcher_llm.invoke([system_msg] + messages)
    return {
        "messages":[response],
        "next_agent":"writer"
    }
    

def writer_agent(state:Agentstate):
    messages = state["messages"]
    system_msg = SystemMessage(content="You are a technical writer. Review the conversation and create a Summary over it")
    # Simple completion without tools.
    response = llm.invoke([system_msg]+messages)
    return {
        "messages":[response],
        "next_agent":"end"
    }
    

# Tool executor node.
def execute_tool(state: Agentstate):
    """Execute any pending tool"""
    messages = state["messages"]
    last_msg = messages[-1]
    # Check if there are tools to execute.
    if hasattr(last_msg,"tool_calls") and last_msg.tool_calls:
        # create tool node and execute.
        tool_node = ToolNode([search_web,write_summary])
        response = tool_node.invoke(state)
        return response
    
    # No tools to execute.
    return state

# Build Graph.
workflow = StateGraph(MessagesState)
# Adding Node in graph.
workflow.add_node("researcher",researcher_agent)
workflow.add_node("writer",writer_agent)
# Define Flow of the graph.
workflow.set_entry_point("researcher")
workflow.add_edge("researcher","writer")
workflow.add_edge("writer",END)
final_work = workflow.compile()

response = final_work.invoke({"messages":"Research about the agent ai uses in Buisness"})
response["messages"][-1].content