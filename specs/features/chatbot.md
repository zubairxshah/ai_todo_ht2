# Feature Spec: AI Chatbot Interface

> Natural language todo management powered by OpenAI Agents SDK and MCP

## Overview

The chatbot provides a conversational interface for managing todos. Users can create, list, complete, update, and delete tasks using natural language instead of traditional UI interactions.

## Agent Behavior Specification

### Identity & Persona

```
You are a helpful todo assistant. You help users manage their tasks through natural conversation.
You have access to tools that let you add, list, complete, update, and delete tasks.
Always confirm actions you take and provide clear summaries.
Be concise but friendly.
```

### Core Capabilities

1. **Task Creation** - Add new todos from natural language
2. **Task Listing** - Show tasks with filters (all, pending, completed)
3. **Task Completion** - Mark tasks as done
4. **Task Updates** - Modify task titles
5. **Task Deletion** - Remove tasks
6. **Conversational Context** - Remember context within a session

### Behavior Rules

| Rule | Description |
|------|-------------|
| Confirm Actions | Always confirm what action was taken |
| Clarify Ambiguity | Ask for clarification when intent is unclear |
| Handle Errors Gracefully | Provide helpful messages when operations fail |
| Respect Boundaries | Only access the current user's tasks |
| Be Concise | Keep responses short and actionable |

## Natural Language Examples

### Adding Tasks

| User Input | Expected Action |
|------------|-----------------|
| "Add buy groceries" | Create task "buy groceries" |
| "I need to call mom tomorrow" | Create task "call mom tomorrow" |
| "Remind me to submit the report" | Create task "submit the report" |
| "Add three tasks: email boss, review PR, update docs" | Create 3 separate tasks |

### Listing Tasks

| User Input | Expected Action |
|------------|-----------------|
| "Show my tasks" | List all tasks |
| "What do I need to do?" | List pending tasks |
| "List completed tasks" | List completed tasks only |
| "Do I have any tasks?" | List all tasks with count |

### Completing Tasks

| User Input | Expected Action |
|------------|-----------------|
| "Mark groceries as done" | Complete task matching "groceries" |
| "I finished the report" | Complete task matching "report" |
| "Done with task 3" | Complete task by position/id |
| "Complete all tasks" | Mark all pending tasks as complete |

### Updating Tasks

| User Input | Expected Action |
|------------|-----------------|
| "Rename groceries to buy vegetables" | Update task title |
| "Change 'call mom' to 'call mom at 5pm'" | Update task with more detail |

### Deleting Tasks

| User Input | Expected Action |
|------------|-----------------|
| "Delete the groceries task" | Remove task matching "groceries" |
| "Remove task 2" | Delete task by position |
| "Clear all completed tasks" | Delete all completed tasks |

### Conversational Context

| Conversation Flow | Expected Behavior |
|-------------------|-------------------|
| "Add meeting with John" → "Make it at 3pm" | Update the just-created task |
| "List tasks" → "Complete the first one" | Complete based on previous listing |
| "What's task 2?" | Refer to numbered list from previous response |

## Error Handling

| Scenario | Response |
|----------|----------|
| Task not found | "I couldn't find a task matching 'X'. Here are your current tasks: ..." |
| Ambiguous match | "I found multiple tasks matching 'X'. Which one did you mean? 1) ... 2) ..." |
| No tasks exist | "You don't have any tasks yet. Would you like to add one?" |
| Permission denied | "I can only access your own tasks." |

## Response Format

### Successful Operations

```
✅ Added task: "buy groceries"

You now have 5 tasks (3 pending, 2 completed).
```

```
📋 Your tasks:

1. [ ] Buy groceries
2. [ ] Call mom
3. [x] Submit report

3 tasks total (2 pending, 1 completed)
```

### Error Responses

```
❌ I couldn't find a task matching "groceries".

Your current tasks are:
1. [ ] Buy vegetables
2. [ ] Call mom

Did you mean "Buy vegetables"?
```

## Security Requirements

- **User Isolation**: Agent can ONLY access tasks belonging to the authenticated user
- **Input Validation**: All user input sanitized before processing
- **No Data Leakage**: Never reveal other users' tasks or system internals
- **Audit Trail**: All operations logged with user_id and timestamp

## Integration Points

- **Authentication**: Uses existing Better Auth JWT flow
- **Database**: Stores conversations in PostgreSQL (Neon)
- **API**: Exposes `/api/chat` endpoint for frontend
- **MCP Tools**: Connects to task CRUD operations via MCP protocol

## Acceptance Criteria

- [ ] User can add tasks via natural language
- [ ] User can list tasks with optional filters
- [ ] User can complete tasks by name or position
- [ ] User can update task titles
- [ ] User can delete tasks
- [ ] Conversations persist within a session
- [ ] Agent only accesses authenticated user's tasks
- [ ] Errors are handled gracefully with helpful messages
