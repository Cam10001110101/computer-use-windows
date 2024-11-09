from langchain_community.tools import DuckDuckGoSearchRun, DuckDuckGoSearchResults

def get_duckduckgo_search_run():
    """
    Initialize and return a DuckDuckGo Search Run tool.
    
    :return: An instance of DuckDuckGoSearchRun tool
    """
    return DuckDuckGoSearchRun()

def get_duckduckgo_search_results():
    """
    Initialize and return a DuckDuckGo Search Results tool.
    
    :return: An instance of DuckDuckGoSearchResults tool
    """
    return DuckDuckGoSearchResults()
