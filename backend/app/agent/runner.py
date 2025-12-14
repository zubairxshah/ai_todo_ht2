"""
OpenAI Agents SDK Runner for Todo Assistant

Handles conversation flow, tool calling, and response generation.
Uses the OpenAI Chat Completions API with function calling.
"""

import json
import os
from typing import Any
from openai import OpenAI

from app.mcp.tools import get_tools, execute_tool


# System prompt defining agent behavior (from @specs/features/chatbot.md)
SYSTEM_PROMPT = """You are a helpful todo assistant. You help users manage their tasks through natural conversation.

You have access to tools that let you add, list, complete, update, and delete tasks.

## Behavior Rules:
1. **Always confirm actions** - Tell the user what you did after each action
2. **Be concise** - Keep responses short and actionable
3. **Handle errors gracefully** - If something fails, explain what went wrong helpfully
4. **Clarify ambiguity** - If multiple tasks match, ask the user to be more specific
5. **Provide context** - After actions, show task counts when relevant

## Response Format Guidelines:
- Use ✅ for successful additions/completions
- Use 📋 for listing tasks
- Use ✏️ for updates
- Use 🗑️ for deletions
- Use ❌ for errors
- Use [ ] for pending tasks and [x] for completed tasks when listing

## Example Responses:

After adding a task:
"✅ Added task: 'buy groceries'

You now have 3 tasks (2 pending, 1 completed)."

When listing tasks:
"📋 Your tasks:

1. [ ] Buy groceries
2. [ ] Call mom
3. [x] Submit report

3 tasks total (2 pending, 1 completed)"

After completing a task:
"✅ Marked 'buy groceries' as done!

You now have 2 pending tasks."

When task not found:
"❌ I couldn't find a task matching 'xyz'.

Your current tasks are:
1. [ ] Buy vegetables
2. [ ] Call mom

Did you mean one of these?"

When multiple matches:
"I found multiple tasks matching 'call':
1. Call mom
2. Call dentist

Which one did you mean?"
"""


def run_agent(
    messages: list[dict[str, Any]],
    user_id: str,
    model: str = "gpt-4o-mini"
) -> tuple[str, list[dict[str, Any]]]:
    """
    Run the agent with conversation history and return response.

    Args:
        messages: List of conversation messages (OpenAI format)
        user_id: Authenticated user's ID (injected into tool calls)
        model: OpenAI model to use

    Returns:
        Tuple of (response_text, actions_taken)
    """
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
    max_iterations = 10  # Prevent infinite loops
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        try:
            # Call OpenAI
            response = client.chat.completions.create(
                model=model,
                messages=full_messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
            )
        except Exception as e:
            return f"❌ Sorry, I encountered an error: {str(e)}", actions_taken

        assistant_message = response.choices[0].message

        # Check if we need to call tools
        if assistant_message.tool_calls:
            # Add assistant message with tool calls to history
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

            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}

                # Execute tool with user_id injection (security: user_id from auth, not AI)
                result = execute_tool(tool_name, arguments, user_id)

                # Track action for response metadata
                actions_taken.append({
                    "tool": tool_name,
                    "input": {k: v for k, v in arguments.items() if k != "user_id"},
                    "result": result
                })

                # Add tool result to messages for next iteration
                full_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })
        else:
            # No tool calls - return the final response
            final_response = assistant_message.content or ""
            if not final_response:
                final_response = "I'm not sure how to help with that. Try asking me to add, list, complete, update, or delete tasks."
            return final_response, actions_taken

    # Max iterations reached (shouldn't happen normally)
    return "❌ I'm having trouble processing your request. Please try again with a simpler request.", actions_taken
