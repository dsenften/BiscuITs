#  Released under MIT License
#
#  Copyright (©) 2025. Talent Factory GmbH
#
#  Permission is hereby granted, free of charge, to any person obtaining
#  a copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#  NON INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.

import os

import logfire
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP

load_dotenv()
logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))

# Follow the steps here to get your Riza remote MCP server URL: https://docs.riza.io/getting-started/mcp-servers
riza_server = MCPServerHTTP(
    url=f'https://mcp.riza.io/code-interpreter?secret={os.getenv("RIZA_TOKEN")}'
)

agent = Agent(
    model="anthropic:claude-3-5-sonnet-latest",
    instrument=True,
    mcp_servers=[riza_server],
)


async def main():
    async with agent.run_mcp_servers():
        result = await agent.run("hello!")
        while True:
            print(f"\n{result.data}")
            user_input = input("\n> ")
            result = await agent.run(user_input, message_history=result.new_messages())


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
