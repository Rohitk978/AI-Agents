from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Math")
@mcp.tool()
def add(a:int,b:int)->int:
    """Add two number
        a: int 
        b: int
    """
    return a+b
@mcp.tool()
def multiply(a:int,b:int)->int:
    """Multiply two number
    a: int
    b: int
    """
    return a*b

# The transport "stdio" tell the  respond to:
# use standard input/output function for recieve and respond to the tool function calls.

if __name__ == "__main__":
    mcp.run(transport="stdio")