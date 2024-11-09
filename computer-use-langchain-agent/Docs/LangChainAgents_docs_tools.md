# How to use chat models to call tools
### Prerequisites
This guide assumes familiarity with the following concepts:

- Chat models
- Tool calling
- Tools
- Output parsers
Tool calling allows a chat model to respond to a given prompt by "calling a tool".  

Remember, while the name "tool calling" implies that the model is directly performing some action, this is actually not the case! The model only generates the arguments to a tool, and actually running the tool (or not) is up to the user.   

Tool calling is a general technique that generates structured output from a model, and you can use it even when you don't intend to invoke any tools. An example use-case of that is extraction from unstructured text.

[Diagram of calling a tool]

If you want to see how to use the model-generated tool call to actually run a tool check out this guide.

Supported models
Tool calling is not universal, but is supported by many popular LLM providers. You can find a list of all models that support tool calling here.

LangChain implements standard interfaces for defining tools, passing them to LLMs, and representing tool calls. This guide will cover how to bind tools to an LLM, then invoke the LLM to generate these arguments.

# Defining tool schemas
For a model to be able to call tools, we need to pass in tool schemas that describe what the tool does and what it's arguments are. Chat models that support tool calling features implement a .bind_tools() method for passing tool schemas to the model. Tool schemas can be passed in as Python functions (with typehints and docstrings), Pydantic models, TypedDict classes, or LangChain Tool objects. Subsequent invocations of the model will pass in these tool schemas along with the prompt.

### Python functions
Our tool schemas can be Python functions:

```python
# The function name, type hints, and docstring are all part of the tool
# schema that's passed to the model. Defining good, descriptive schemas
# is an extension of prompt engineering and is an important part of
# getting models to perform well.
def add(a: int, b: int) -> int:
    """Add two integers.

    Args:
        a: First integer
        b: Second integer
    """
    return a + b


def multiply(a: int, b: int) -> int:
    """Multiply two integers.

    Args:
        a: First integer
        b: Second integer
    """
    return a * b
```

# LangChain Tool
LangChain also implements a ```@tool decorator``` that allows for further control of the tool schema, such as tool names and argument descriptions. See the how-to guide here for details.

# Pydantic class
You can equivalently define the schemas without the accompanying functions using Pydantic.

Note that all fields are required unless provided a default value.

```python
from pydantic import BaseModel, Field


class add(BaseModel):
    """Add two integers."""

    a: int = Field(..., description="First integer")
    b: int = Field(..., description="Second integer")


class multiply(BaseModel):
    """Multiply two integers."""

    a: int = Field(..., description="First integer")
    b: int = Field(..., description="Second integer")
```

# TypedDict class
Requires langchain-core>=0.2.25
Or using TypedDicts and annotations:

```python
from typing_extensions import Annotated, TypedDict


class add(TypedDict):
    """Add two integers."""

    # Annotations must have the type and can optionally include a default value and description (in that order).
    a: Annotated[int, ..., "First integer"]
    b: Annotated[int, ..., "Second integer"]


class multiply(TypedDict):
    """Multiply two integers."""

    a: Annotated[int, ..., "First integer"]
    b: Annotated[int, ..., "Second integer"]


tools = [add, multiply]
```

To actually bind those schemas to a chat model, we'll use the ```.bind_tools()``` method. This handles converting the ```add``` and ```multiply``` schemas to the proper format for the model. The tool schema will then be passed it in each time the model is invoked.

- OpenAI
- Anthropic
- Azure
- Google
- Cohere
- NVIDIA
- FireworksAI
- Groq
- MistralAI
- TogetherAI


```python
pip install -qU langchain-anthropic
```

```python
import getpass
import os

os.environ["ANTHROPIC_API_KEY"] = getpass.getpass()

from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
```

```python
llm_with_tools = llm.bind_tools(tools)

query = "What is 3 * 12?"

llm_with_tools.invoke(query)
```

```cs
AIMessage(content='', additional_kwargs={'tool_calls': [{'id': 'call_iXj4DiW1p7WLjTAQMRO0jxMs', 'function': {'arguments': '{"a":3,"b":12}', 'name': 'multiply'}, 'type': 'function'}], 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 17, 'prompt_tokens': 80, 'total_tokens': 97}, 'model_name': 'gpt-4o-mini-2024-07-18', 'system_fingerprint': 'fp_483d39d857', 'finish_reason': 'tool_calls', 'logprobs': None}, id='run-0b620986-3f62-4df7-9ba3-4595089f9ad4-0', tool_calls=[{'name': 'multiply', 'args': {'a': 3, 'b': 12}, 'id': 'call_iXj4DiW1p7WLjTAQMRO0jxMs', 'type': 'tool_call'}], usage_metadata={'input_tokens': 80, 'output_tokens': 17, 'total_tokens': 97})
```

As we can see our LLM generated arguments to a tool! You can look at the docs for bind_tools() to learn about all the ways to customize how your LLM selects tools, as well as this guide on how to force the LLM to call a tool rather than letting it decide.

# Tool calls
If tool calls are included in a LLM response, they are attached to the corresponding message or message chunk as a list of tool call objects in the .tool_calls attribute.

Note that chat models can call multiple tools at once.

A ```ToolCall``` is a typed dict that includes a tool name, dict of argument values, and (optionally) an identifier. Messages with no tool calls default to an empty list for this attribute.

```python
query = "What is 3 * 12? Also, what is 11 + 49?"

llm_with_tools.invoke(query).tool_calls
```

```
[{'name': 'multiply',
  'args': {'a': 3, 'b': 12},
  'id': 'call_1fyhJAbJHuKQe6n0PacubGsL',
  'type': 'tool_call'},
 {'name': 'add',
  'args': {'a': 11, 'b': 49},
  'id': 'call_fc2jVkKzwuPWyU7kS9qn1hyG',
  'type': 'tool_call'}]
```

The ```.tool_calls``` attribute should contain valid tool calls. Note that on occasion, model providers may output malformed tool calls (e.g., arguments that are not valid JSON). When parsing fails in these cases, instances of ```InvalidToolCall``` are populated in the ```.invalid_tool_calls``` attribute. An InvalidToolCall can have a name, string arguments, identifier, and error message.


# Parsing
If desired, output parsers can further process the output. For example, we can convert existing values populated on the .tool_calls to Pydantic objects using the PydanticToolsParser:

```python
from langchain_core.output_parsers import PydanticToolsParser
from pydantic import BaseModel, Field


class add(BaseModel):
    """Add two integers."""

    a: int = Field(..., description="First integer")
    b: int = Field(..., description="Second integer")


class multiply(BaseModel):
    """Multiply two integers."""

    a: int = Field(..., description="First integer")
    b: int = Field(..., description="Second integer")


chain = llm_with_tools | PydanticToolsParser(tools=[add, multiply])
chain.invoke(query)
```

##### API Reference:PydanticToolsParser
```python
[multiply(a=3, b=12), add(a=11, b=49)]
```

# Next steps
Now you've learned how to bind tool schemas to a chat model and have the model call the tool.

Next, check out this guide on actually using the tool by invoking the function and passing the results back to the model:

- Pass tool results back to model
You can also check out some more specific uses of tool calling:

- Getting structured outputs from models
- Few shot prompting with tools
- Stream tool calls
- Pass runtime values to tools








# Toolkits
Toolkits are collections of tools that are designed to be used together for specific tasks. They have convenient loading methods. For a complete list of available ready-made toolkits, visit Integrations.

All Toolkits expose a get_tools method which returns a list of tools. You can therefore do:

```python
# Initialize a toolkit
toolkit = ExampleTookit(...)

# Get list of tools
tools = toolkit.get_tools()

# Create agent
agent = create_agent_method(llm, tools, prompt)
```



# Defining Custom Tools
When constructing your own agent, you will need to provide it with a list of Tools that it can use. Besides the actual function that is called, the Tool consists of several components:

```name``` (str), is required and must be unique within a set of tools provided to an agent  
```description``` (str), is optional but recommended, as it is used by an agent to determine tool use  
```args_schema``` (Pydantic BaseModel), is optional but recommended, can be used to provide more information (e.g.,  few-shot examples) or validation for expected parameters.   

There are multiple ways to define a tool. In this guide, we will walk through how to do for two functions:

A made up search function that always returns the string "LangChain"
A multiplier function that will multiply two numbers by eachother
The biggest difference here is that the first function only requires one input, while the second one requires multiple. Many agents only work with functions that require single inputs, so it's important to know how to work with those. For the most part, defining these custom tools is the same, but there are some differences.

```python
# Import things that are needed generically
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
```

##### API Reference:
- BaseTool
- StructuredTool
- tool

# @tool decorator
This @tool decorator is the simplest way to define a custom tool. The decorator uses the function name as the tool name by default, but this can be overridden by passing a string as the first argument. Additionally, the decorator will use the function's docstring as the tool's description - so a docstring MUST be provided.

```python
@tool
def search(query: str) -> str:
    """Look up things online."""
    return "LangChain"
```
```python
print(search.name)
print(search.description)
print(search.args)
```
```python
search
search(query: str) -> str - Look up things online.
{'query': {'title': 'Query', 'type': 'string'}}
```

```python
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b
```

```python
print(multiply.name)
print(multiply.description)
print(multiply.args)
```

```python
multiply
multiply(a: int, b: int) -> int - Multiply two numbers.
{'a': {'title': 'A', 'type': 'integer'}, 'b': {'title': 'B', 'type': 'integer'}}
```

You can also customize the tool name and JSON args by passing them into the tool decorator.

```python
class SearchInput(BaseModel):
    query: str = Field(description="should be a search query")


@tool("search-tool", args_schema=SearchInput, return_direct=True)
def search(query: str) -> str:
    """Look up things online."""
    return "LangChain"
```

```python
print(search.name)
print(search.description)
print(search.args)
print(search.return_direct)

search-tool
search-tool(query: str) -> str - Look up things online.
{'query': {'title': 'Query', 'description': 'should be a search query', 'type': 'string'}}
True
```

# Subclass BaseTool
You can also explicitly define a custom tool by subclassing the BaseTool class. This provides maximal control over the tool definition, but is a bit more work.


```python
from typing import Optional, Type

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)


class SearchInput(BaseModel):
    query: str = Field(description="should be a search query")


class CalculatorInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")


class CustomSearchTool(BaseTool):
    name = "custom_search"
    description = "useful for when you need to answer questions about current events"
    args_schema: Type[BaseModel] = SearchInput

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        return "LangChain"

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")


class CustomCalculatorTool(BaseTool):
    name = "Calculator"
    description = "useful for when you need to answer questions about math"
    args_schema: Type[BaseModel] = CalculatorInput
    return_direct: bool = True

    def _run(
        self, a: int, b: int, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        return a * b

    async def _arun(
        self,
        a: int,
        b: int,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Calculator does not support async")
```

##### API Reference:
- AsyncCallbackManagerForToolRun
- CallbackManagerForToolRun

```python
search = CustomSearchTool()
print(search.name)
print(search.description)
print(search.args)
```

```python
custom_search
useful for when you need to answer questions about current events
{'query': {'title': 'Query', 'description': 'should be a search query', 'type': 'string'}}
```

```python
multiply = CustomCalculatorTool()
print(multiply.name)
print(multiply.description)
print(multiply.args)
print(multiply.return_direct)
```

```python
Calculator
useful for when you need to answer questions about math
{'a': {'title': 'A', 'description': 'first number', 'type': 'integer'}, 'b': {'title': 'B', 'description': 'second number', 'type': 'integer'}}
True
```

# StructuredTool dataclass
You can also use a ```StructuredTool``` dataclass. This methods is a mix between the previous two. It's more convenient than inheriting from the BaseTool class, but provides more functionality than just using a decorator.

```python
def search_function(query: str):
    return "LangChain"


search = StructuredTool.from_function(
    func=search_function,
    name="Search",
    description="useful for when you need to answer questions about current events",
    # coroutine= ... <- you can specify an async method if desired as well
)
```

```python
print(search.name)
print(search.description)
print(search.args)
```

```python
Search
Search(query: str) - useful for when you need to answer questions about current events
{'query': {'title': 'Query', 'type': 'string'}}
```

You can also define a custom ```args_schema``` to provide more information about inputs.

```python
class CalculatorInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")


def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


calculator = StructuredTool.from_function(
    func=multiply,
    name="Calculator",
    description="multiply numbers",
    args_schema=CalculatorInput,
    return_direct=True,
    # coroutine= ... <- you can specify an async method if desired as well
)
```
```python
print(calculator.name)
print(calculator.description)
print(calculator.args)
```

```python
Calculator
Calculator(a: int, b: int) -> int - multiply numbers
{'a': {'title': 'A', 'description': 'first number', 'type': 'integer'}, 'b': {'title': 'B', 'description': 'second number', 'type': 'integer'}}
```

# Handling Tool Errors
When a tool encounters an error and the exception is not caught, the agent will stop executing. If you want the agent to continue execution, you can raise a ```ToolException``` and set ```handle_tool_error``` accordingly.

When ```ToolException``` is thrown, the agent will not stop working, but will handle the exception according to the ```handle_tool_error``` variable of the tool, and the processing result will be returned to the agent as observation, and printed in red.

You can set ```handle_tool_error``` to ```True```, set it a unified string value, or set it as a function. If it's set as a function, the function should take a ToolException as a parameter and return a ```str``` value.

Please note that only raising a ```ToolException``` won't be effective. You need to first set the ```handle_tool_error``` of the tool because its default value is ```False```.

```python
from langchain_core.tools import ToolException


def search_tool1(s: str):
    raise ToolException("The search tool1 is not available.")
```


##### API Reference:
- ToolException
First, let's see what happens if we don't set handle_tool_error - it will error.

```python
search = StructuredTool.from_function(
    func=search_tool1,
    name="Search_tool1",
    description="A bad tool",
)

search.run("test")
```
```python
[Long verbose error placeholder]Error: ToolException: The search tool1 is not available.
```

Now, let's set handle_tool_error to be True

```python
search = StructuredTool.from_function(
    func=search_tool1,
    name="Search_tool1",
    description="A bad tool",
    handle_tool_error=True,
)

search.run("test")


'The search tool1 is not available.'

We can also define a custom way to handle the tool error

```python
def _handle_error(error: ToolException) -> str:
    return (
        "The following errors occurred during tool execution:"
        + error.args[0]
        + "Please try another tool."
    )


search = StructuredTool.from_function(
    func=search_tool1,
    name="Search_tool1",
    description="A bad tool",
    handle_tool_error=_handle_error,
)

search.run("test")
```

```python
'The following errors occurred during tool execution:The search tool1 is not available.Please try another tool.'
```


