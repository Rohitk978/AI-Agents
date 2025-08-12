import asyncio
import os
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve and validate Groq API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set")
print(f"API Key: {api_key}")  # Debug

async def main():
    # Initialize MCP client
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["D:/Coding/Agent AI/MCPServer&Client/mathserver.py"],
                "transport": "stdio"
            },
            "weather": {
                "url": "http://127.0.0.1:8000/",
                "transport": "streamable_http"
            }
        }
    )

    # Load tools from MCP servers
    try:
        math_tools = []
        weather_tools = []
        async with client.session("math") as session:
            math_tools = await load_mcp_tools(session)
        async with client.session("weather") as session:
            weather_tools = await load_mcp_tools(session)
        tools = math_tools + weather_tools
        print(f"Loaded tools: {[tool.name for tool in tools]}")  # Debug
    except Exception as e:
        print(f"Error loading MCP tools: {e}")
        raise

    # Initialize ChatGroq with a valid model
    model = ChatGroq(model="llama3-8b-8192", api_key=api_key)

    # Create the agent
    agent = create_react_agent(model, tools)

    # Example input
    input_message = {"messages": [{"role": "user", "content": "What is (3 + 5) / 2?"}]}
    try:
        # Invoke the agent
        math_response = await agent.ainvoke(input_message)
        print("Math Response:", math_response["messages"][-1].content)
    except Exception as e:
        print(f"Error invoking agent: {e}")
        raise

# Run the async function
if __name__ == "__main__":
    asyncio.run(main())