"""
OpenAI Agents SDK Runner for Todo Assistant

Uses the OpenAI Agents SDK with MCP server connection for automatic
tool discovery and execution. The agent connects to the local MCP
server to access task management tools.

Key features:
- Automatic tool discovery via MCP protocol
- Context passing for user_id (security)
- Async execution with Runner.run()
- Action tracking for UI updates
"""

import os
from typing import Any


# System prompt defining agent behavior
SYSTEM_PROMPT = """You are a helpful todo assistant. You help users manage their tasks through natural conversation.

You have access to tools that let you add, list, complete, update, and delete tasks.

## CRITICAL RULE - ALWAYS USE TOOLS:
**You MUST call the appropriate tool for EVERY task-related request.** Never respond based on conversation history or previous tool results. Each user request requires a fresh tool call.

- If user asks to ADD a task → ALWAYS call add_task tool
- If user asks to LIST tasks → ALWAYS call list_tasks tool
- If user asks to COMPLETE a task → ALWAYS call complete_task tool
- If user asks to UPDATE a task → ALWAYS call update_task tool
- If user asks to DELETE a task → ALWAYS call delete_task tool
- If user asks about TAGS → ALWAYS call manage_tags tool

Do NOT assume you know the current state of tasks. Do NOT respond with "I added..." without actually calling the tool. The database is the source of truth, not conversation history.

## Behavior Rules:
1. **Always use tools** - Call the tool for every action, even if similar to a previous request
2. **Always confirm actions** - Tell the user what you did after each action
3. **Be concise** - Keep responses short and actionable
4. **Handle errors gracefully** - If something fails, explain what went wrong helpfully
5. **Clarify ambiguity** - If multiple tasks match, ask the user to be more specific
6. **Provide context** - After actions, show task counts when relevant

## Response Format Guidelines:
- Use checkmarks for successful additions/completions
- Use list icons for listing tasks
- Use edit icons for updates
- Use delete icons for deletions
- Use error icons for errors
- Use [ ] for pending tasks and [x] for completed tasks when listing

## Example Responses:

After adding a task:
"Added task: 'buy groceries'

You now have 3 tasks (2 pending, 1 completed)."

When listing tasks:
"Your tasks:

1. [ ] Buy groceries
2. [ ] Call mom
3. [x] Submit report

3 tasks total (2 pending, 1 completed)"

After completing a task:
"Marked 'buy groceries' as done!

You now have 2 pending tasks."

When task not found:
"I couldn't find a task matching 'xyz'.

Your current tasks are:
1. [ ] Buy vegetables
2. [ ] Call mom

Did you mean one of these?"

When multiple matches:
"I found multiple tasks matching 'call':
1. Call mom
2. Call dentist

Which one did you mean?"

## Important:
- The user_id parameter is automatically injected for security
- Never ask the user for their user_id
- All tool calls are scoped to the authenticated user
"""


async def run_agent(
    messages: list[dict[str, Any]],
    user_id: str,
    model: str = "gpt-4o-mini"
) -> tuple[str, list[dict[str, Any]]]:
    """
    Run the agent with conversation history and return response.

    Uses direct OpenAI API with function calling for reliable operation.
    The user_id is injected into all tool calls for security.

    Args:
        messages: List of conversation messages (OpenAI format)
        user_id: Authenticated user's ID (from JWT, injected into tools)
        model: OpenAI model to use

    Returns:
        Tuple of (response_text, actions_taken)
    """
    # Use the reliable direct OpenAI implementation
    return _run_agent_direct(messages, user_id, model)


# Keep synchronous wrapper for backward compatibility
def run_agent_sync(
    messages: list[dict[str, Any]],
    user_id: str,
    model: str = "gpt-4o-mini"
) -> tuple[str, list[dict[str, Any]]]:
    """
    Synchronous wrapper for run_agent.

    For use in non-async contexts.
    """
    return _run_agent_direct(messages, user_id, model)


def _run_agent_direct(
    messages: list[dict[str, Any]],
    user_id: str,
    model: str = "gpt-4o-mini"
) -> tuple[str, list[dict[str, Any]]]:
    """
    Direct implementation using OpenAI API with function calling.

    This is the reliable, tested implementation that handles
    tool calling through the OpenAI Chat Completions API.
    """
    import json
    from openai import OpenAI
    from app.mcp.tools import get_tools, execute_tool

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    tools = get_tools()
    actions_taken = []

    # Prepare messages with system prompt
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add conversation history (skip any existing system messages)
    for msg in messages:
        if msg.get("role") != "system":
            full_messages.append(msg)

    # Run conversation loop (handle tool calls)
    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        try:
            response = client.chat.completions.create(
                model=model,
                messages=full_messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
            )
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}", actions_taken

        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            tool_calls_data = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in assistant_message.tool_calls
            ]

            full_messages.append({
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": tool_calls_data
            })

            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}

                result = execute_tool(tool_name, arguments, user_id)

                actions_taken.append({
                    "tool": tool_name,
                    "input": {k: v for k, v in arguments.items() if k != "user_id"},
                    "result": result
                })

                full_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })
        else:
            final_response = assistant_message.content or ""
            if not final_response:
                final_response = "I'm not sure how to help with that. Try asking me to add, list, complete, update, or delete tasks."
            return final_response, actions_taken

    return "I'm having trouble processing your request. Please try again with a simpler request.", actions_taken
