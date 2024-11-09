from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type, Annotated
from markdownify import markdownify as md
from langchain_community.document_loaders import FireCrawlLoader
import os
from datetime import datetime
from urllib.parse import urlparse

class FirecrawlInput(BaseModel):
    url: str = Field(..., description="The URL to scrape")
    api_key: Optional[str] = Field(None, description="Optional FireCrawl API key. If not provided, will use environment variable.")

def get_firecrawl_tool() -> BaseTool:
    """Returns a FireCrawl tool for scraping web pages and saving them as markdown."""
    
    class FirecrawlTool(BaseTool):
        name: str = "firecrawl"
        description: str = "Scrapes a web page and saves it as a markdown file in the Output/Firecrawl directory"
        args_schema: Type[BaseModel] = FirecrawlInput
        
        def _run(self, url: str, api_key: Optional[str] = None) -> str:
            # Use provided API key or get from environment
            api_key = api_key or os.getenv('FIRECRAWL_API_KEY')
            
            # Initialize the FireCrawlLoader
            firecrawl_loader = FireCrawlLoader(
                api_key=api_key,
                url=url,
                mode="scrape"
            )
            
            # Load documents from the URL
            documents = firecrawl_loader.load()
            
            # Generate filename from URL path
            parsed_url = urlparse(url)
            path_parts = [part for part in parsed_url.path.split('/') if part]
            content_name = '_'.join(path_parts) if path_parts else 'index'
            
            # Create filename with date prefix
            date_prefix = datetime.now().strftime("%Y-%m-%d")
            output_dir = os.path.join("Output", "firecrawl")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{date_prefix}_{content_name}.md")
            
            # Convert the HTML content to Markdown and save
            if documents:
                html_content = documents[0].page_content
                markdown_content = md(html_content)
                
                with open(output_path, 'w', encoding='utf-8') as md_file:
                    md_file.write(markdown_content)
                return f"Successfully saved markdown file to: {output_path}"
            else:
                return "No documents found."
        
        def _arun(self, url: str, api_key: Optional[str] = None) -> str:
            raise NotImplementedError("FirecrawlTool does not support async execution")
    
    return FirecrawlTool()
