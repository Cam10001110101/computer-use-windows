import os
import yaml
from typing import Annotated, TypedDict, Any
from dotenv import load_dotenv
from pprint import pprint

from langchain_anthropic import ChatAnthropic
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.globals import set_llm_cache
from langchain_community.cache import SQLiteCache

# Import search tools
from Tools.TavilySearchResults import get_tavily_search_tool
from Tools.BraveSearch import get_brave_search_tool
from Tools.DuckDuckGoSearch import get_duckduckgo_search_run
from Tools.WikipediaSearch import get_wikipedia_search_tool
from Tools.FirecrawlTool import get_firecrawl_tool

# Import computer use tools
from Tools.computer import ComputerTool
from Tools.bash import BashTool
from Tools.edit import EditTool
from Tools.collection import ToolCollection

# Set up SQLite caching
set_llm_cache(SQLiteCache(database_path="Agent/.langchain.db"))

# Define a basic ConfigSchema
class ConfigSchema(TypedDict):
    configurable: dict[str, Any]

# Define the state structure
class State(TypedDict):
    messages: Annotated[list, add_messages]

def load_environment():
    load_dotenv()
    return {
        'LANGSMITH_API_KEY': os.getenv('LANGSMITH_API_KEY'),
        'TAVILY_API_KEY': os.getenv('TAVILY_API_KEY'),
        'BRAVE_API_KEY': os.getenv('BRAVE_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY')
    }

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)

def setup_graph():
    env_vars = load_environment()
    config = load_config()
    checkpointer = MemorySaver()
    graph_builder = StateGraph(State, config_schema=ConfigSchema)

    # Set up search and utility tools
    tavily_tool = get_tavily_search_tool()
    brave_tool = get_brave_search_tool(env_vars['BRAVE_API_KEY'])
    duckduckgo_tool = get_duckduckgo_search_run()
    wikipedia_tool = get_wikipedia_search_tool()
    firecrawl_tool = get_firecrawl_tool()
    
    # Create computer use tools collection
    tool_collection = ToolCollection(
        computer_tool=ComputerTool(),
        bash_tool=BashTool(),
        edit_tool=EditTool()
    )
    
    # Convert tool collection to LangChain format
    computer_tools = [
        tool for tool in tool_collection.tools.values()
    ]
    
    # Combine all tools
    tools = [
        tavily_tool,
        brave_tool,
        duckduckgo_tool,
        wikipedia_tool,
        firecrawl_tool,
        *computer_tools
    ]
    
    # Initialize LLM with computer use capabilities
    llm = ChatAnthropic(
        anthropic_api_key=env_vars['ANTHROPIC_API_KEY'],
        model=config['models']['anthropic']['name'],
        temperature=config['models']['anthropic']['temperature'],
        model_kwargs={
            "system": """You have access to computer use tools that allow you to interact with the computer.
            You can use the mouse, keyboard, take screenshots, edit files, and run bash commands.
            Always verify the results of your actions before proceeding to the next step."""
        }
    )
    llm_with_tools = llm.bind_tools(tools)

    def chatbot(state: State):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    # Set up graph nodes
    graph_builder.add_node("chatbot", chatbot)
    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)

    # Configure graph edges
    graph_builder.add_conditional_edges("chatbot", tools_condition)
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")

    return graph_builder.compile(checkpointer=checkpointer)

def handle_input(graph, user_input, config):
    events = graph.stream({"messages": [("human", user_input)]}, config, stream_mode="values")
    for event in events:
        content = event['messages'][-1].content
        print("Assistant:")
        if isinstance(content, str):
            print(content)
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    pprint(item, indent=2, width=120)
                else:
                    print(item)
        else:
            pprint(content, indent=2, width=120)

def print_state_history(graph, config):
    history = graph.get_state_history(config)
    print("State history:")
    for idx, state in enumerate(history):
        print(f"Checkpoint {idx}:")
        pprint(state, indent=2, width=120)
        print()

def main():
    env_vars = load_environment()
    graph = setup_graph()
    config = {"configurable": {"thread_id": "1"}}

    print("Anthropic Chatbot initialized with computer use capabilities. Type 'quit' to exit or 'rewind' to time travel.")
    while True:
        user_input = input("User: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        elif user_input.lower() == "rewind":
            print_state_history(graph, config)
            checkpoint_idx = int(input("Enter checkpoint index to rewind to: "))
            history = graph.get_state_history(config)
            if 0 <= checkpoint_idx < len(history):
                graph.resume_from_state(history[checkpoint_idx], config)
            else:
                print("Invalid checkpoint index.")
        else:
            handle_input(graph, user_input, config)

    snapshot = graph.get_state(config)
    print("Final state snapshot:")
    pprint(snapshot, indent=2, width=120)
    if snapshot.next:
        print("Next node:", snapshot.next)
    else:
        print("No next node. The graph has ended this turn.")

if __name__ == "__main__":
    main()
