from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

def get_wikipedia_search_tool():
    """
    Initialize and return a Wikipedia Search tool.
    
    :return: An instance of WikipediaQueryRun tool
    """
    return WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
