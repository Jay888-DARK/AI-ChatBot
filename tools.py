from langchain.tools import Tool
import wikipedia

def search_tool_func(query):
    return f"Search results for '{query}' are not yet implemented."

def wiki_tool_func(query):
    return wikipedia.summary(query, sentences=2)

def save_tool_func(data):
    with open("research_output.txt", "a", encoding="utf-8") as f:
        f.write(data + "\n")
    return "Saved successfully!"

search_tool = Tool(
    name="Search Tool",
    func=search_tool_func,
    description="Search the web for recent or specific information"
)

wiki_tool = Tool(
    name="Wikipedia Tool",
    func=wiki_tool_func,
    description="Fetch general information from Wikipedia"
)

save_tool = Tool(
    name="Save Tool",
    func=save_tool_func,
    description="Save the research result into a file"
)
