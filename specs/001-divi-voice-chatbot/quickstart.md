# Quickstart: Testing Divi Voice Chatbot

**Feature**: 001-divi-voice-chatbot
**Date**: 2025-12-21

## Prerequisites

1. **Microphone**: Working microphone connected to your device
2. **Browser**: Chrome, Edge, or Safari (Firefox has limited support)
3. **Environment**: Quiet room for best recognition accuracy
4. **Backend Running**: `uvicorn app.main:app --reload` on port 8000
5. **Frontend Running**: `npm run dev` on port 3000
6. **Logged In**: Valid user session in the app

---

## Test Scenarios

### Scenario 1: Basic Voice Task Creation (P1)

**Goal**: Verify voice-to-task flow works end-to-end

**Steps**:
1. Navigate to Dashboard
2. Open Chat Widget (click chat icon)
3. Click the microphone button
4. Grant microphone permission if prompted
5. Say: "Add task buy groceries"
6. Wait for transcription to appear
7. Observe Divi's response

**Expected Results**:
- [ ] Microphone icon shows "Listening..." state (blue pulsing)
- [ ] Transcription appears: "Add task buy groceries"
- [ ] Divi responds: "Created task: buy groceries"
- [ ] Task appears in task list on dashboard
- [ ] Microphone returns to idle state

---

### Scenario 2: Voice Task Query (P1)

**Goal**: Verify voice queries return task list

**Steps**:
1. Ensure you have at least 2 tasks in your list
2. Click microphone button
3. Say: "Show my tasks"
4. Wait for response

**Expected Results**:
- [ ] Transcription appears: "Show my tasks"
- [ ] Divi responds with list of your tasks
- [ ] Tasks displayed in chat message

**Variations**:
- "What's on my list?"
- "Show high priority tasks"
- "What do I need to do today?"

---

### Scenario 3: Voice Task Completion (P2)

**Goal**: Verify voice can mark tasks complete

**Steps**:
1. Create a task named "test task"
2. Click microphone button
3. Say: "Mark test task as done"
4. Wait for response

**Expected Results**:
- [ ] Transcription appears correctly
- [ ] Divi responds: "Marked 'test task' as complete"
- [ ] Task shows as completed in dashboard
- [ ] Task notification appears (blue pill)

---

### Scenario 4: Visual Feedback States (P2)

**Goal**: Verify all visual states display correctly

**Test 4a: Listening State**
1. Click microphone
2. Observe: Blue pulsing indicator, "Listening..." text

**Test 4b: Processing State**
1. Finish speaking (pause for 2 seconds)
2. Observe: Spinner icon, "Processing..." text

**Test 4c: Response State**
1. Wait for Divi's response
2. Observe: Response appears with Divi attribution

**Expected Results**:
- [ ] Each state visually distinct
- [ ] Transitions are smooth (< 500ms)
- [ ] No flickering between states

---

### Scenario 5: Error Handling (P3)

**Test 5a: Permission Denied**
1. Revoke microphone permission in browser settings
2. Click microphone button
3. Observe error message

**Test 5b: No Speech**
1. Click microphone button
2. Don't speak for 10 seconds
3. Observe timeout handling

**Test 5c: Cancel Recording**
1. Click microphone button
2. Start speaking
3. Click microphone button again (cancel)
4. Observe cancellation

**Expected Results**:
- [ ] Permission denied: Shows "Microphone access required" message
- [ ] No speech: Shows "No speech detected" after timeout
- [ ] Cancel: Returns to idle state, no transcription sent

---

### Scenario 6: Fallback to Text (P3)

**Goal**: Verify text input still works alongside voice

**Steps**:
1. With voice feature visible
2. Type in text input: "Add task from text"
3. Press Enter

**Expected Results**:
- [ ] Text input works normally
- [ ] Divi processes text command
- [ ] Task created successfully
- [ ] Voice and text coexist in UI

---

## Browser Compatibility Matrix

| Browser | Web Speech API | Expected Behavior |
|---------|---------------|-------------------|
| Chrome 90+ | Yes | Full voice support |
| Edge 90+ | Yes | Full voice support |
| Safari 14.1+ | Yes (prefixed) | Full voice support |
| Firefox 90+ | Limited | Falls back to Whisper API |
| Mobile Chrome | Yes | Full voice support |
| Mobile Safari | Yes | Full voice support |

---

## Troubleshooting

### "Microphone not working"
1. Check browser permissions (Settings > Privacy > Microphone)
2. Ensure microphone is not muted at OS level
3. Try a different browser

### "No speech detected"
1. Speak louder/clearer
2. Reduce background noise
3. Move closer to microphone
4. Check microphone input level in OS settings

### "Transcription is inaccurate"
1. Speak more slowly
2. Enunciate clearly
3. Use simple, direct commands
4. Reduce background noise

### "Voice button doesn't appear"
1. Check browser console for errors
2. Verify feature flag is enabled (if applicable)
3. Clear browser cache and reload

---

## Performance Benchmarks

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Click-to-listening | < 500ms | Stopwatch from click to visual feedback |
| Transcription latency | < 2s | Time from speech end to text appearing |
| End-to-end task creation | < 10s | Click mic → task in list |
| Accuracy | > 90% | Count correct transcriptions / total |

---

## Sign-off Checklist

Before marking feature complete:

- [ ] All P1 scenarios pass
- [ ] All P2 scenarios pass
- [ ] Critical P3 error scenarios pass
- [ ] Works on Chrome, Edge, Safari
- [ ] Performance targets met
- [ ] No console errors during normal use
