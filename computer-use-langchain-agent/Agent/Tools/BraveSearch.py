from langchain_community.tools import BraveSearch

def get_brave_search_tool(api_key):
    """
    Initialize and return a Brave Search tool.
    
    :param api_key: The API key for Brave Search
    :return: An instance of BraveSearch tool
    """
    return BraveSearch.from_api_key(api_key=api_key, search_kwargs={"count": 3})
