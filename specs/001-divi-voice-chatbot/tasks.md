# Tasks: Divi Voice Chatbot

**Input**: Design documents from `/specs/001-divi-voice-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/
**Status**: Ready for Implementation
**Created**: 2025-12-21

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create new files and types needed for voice functionality

- [x] T001 [P] Create voice types file with VoiceState, VoiceError, VoiceInputConfig interfaces in frontend/src/types/voice.ts
- [x] T002 [P] Create TranscriptionResponse and TranscriptionError Pydantic models in backend/app/schemas/transcription.py
- [x] T003 [P] Add OPENAI_API_KEY to backend environment config in backend/app/config.py (if not already present)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core voice infrastructure that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create useVoiceInput hook skeleton with state management in frontend/src/hooks/useVoiceInput.ts
- [x] T005 Create voice-transcription service with Web Speech API detection in frontend/src/lib/voice-transcription.ts
- [x] T006 [P] Create Whisper service for OpenAI API integration in backend/app/services/whisper.py
- [x] T007 Create transcription router with POST /api/transcribe endpoint in backend/app/routers/transcription.py
- [x] T008 Register transcription router in backend/app/main.py
- [x] T009 Create VoiceInput component skeleton in frontend/src/components/Chat/VoiceInput.tsx
- [x] T010 Create VoiceIndicator component for visual states in frontend/src/components/Chat/VoiceIndicator.tsx

**Checkpoint**: Voice infrastructure ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Voice Command for Task Creation (Priority: P1)

**Goal**: Users can speak to create tasks via voice commands

**Independent Test**: Click mic button, say "Add task buy groceries", verify task appears in list

### Implementation for User Story 1

- [x] T011 [US1] Implement Web Speech API recognition in useVoiceInput hook with startListening/stopListening in frontend/src/hooks/useVoiceInput.ts
- [x] T012 [US1] Add microphone permission handling to useVoiceInput hook in frontend/src/hooks/useVoiceInput.ts
- [x] T013 [US1] Implement speech recognition event handlers (onresult, onerror, onend) in frontend/src/hooks/useVoiceInput.ts
- [x] T014 [US1] Add microphone button to ChatKitWidget input area in frontend/src/components/Chat/ChatKitWidget.tsx
- [x] T015 [US1] Integrate VoiceInput component with ChatKitWidget in frontend/src/components/Chat/ChatKitWidget.tsx
- [x] T016 [US1] Connect voice transcription to existing chat submission flow in frontend/src/components/Chat/ChatKitWidget.tsx
- [x] T017 [US1] Add voice input button styling (idle state) with Tailwind in frontend/src/components/Chat/VoiceInput.tsx

**Checkpoint**: Users can create tasks via voice - MVP complete

---

## Phase 4: User Story 2 - Voice Query for Task List (Priority: P1)

**Goal**: Users can ask to see their tasks via voice

**Independent Test**: Say "Show my tasks", verify task list displayed in chat

### Implementation for User Story 2

- [x] T018 [US2] Verify voice transcription works with list commands in frontend/src/hooks/useVoiceInput.ts
- [x] T019 [US2] Test voice flow with "Show my tasks" and "Show high priority tasks" commands
- [x] T020 [US2] Add interim results display during speech recognition in frontend/src/components/Chat/VoiceInput.tsx

**Checkpoint**: Users can query tasks via voice

---

## Phase 5: User Story 3 - Voice Command for Task Completion (Priority: P2)

**Goal**: Users can mark tasks complete via voice

**Independent Test**: Say "Mark buy groceries as done", verify task marked complete

### Implementation for User Story 3

- [x] T021 [US3] Test voice flow with completion commands ("Mark X as done", "Complete X")
- [x] T022 [US3] Handle ambiguous task matching feedback in chat display

**Checkpoint**: Users can complete tasks via voice

---

## Phase 6: User Story 4 - Visual Feedback During Voice Interaction (Priority: P2)

**Goal**: Clear visual indicators for listening, processing, and response states

**Independent Test**: Click mic and observe visual states change appropriately

### Implementation for User Story 4

- [x] T023 [US4] Implement listening state animation (pulsing blue) in frontend/src/components/Chat/VoiceIndicator.tsx
- [x] T024 [US4] Implement processing state animation (spinner) in frontend/src/components/Chat/VoiceIndicator.tsx
- [x] T025 [US4] Implement error state display (red with message) in frontend/src/components/Chat/VoiceIndicator.tsx
- [x] T026 [US4] Add state transition animations with Tailwind keyframes in frontend/tailwind.config.ts
- [x] T027 [US4] Display transcription text while processing in frontend/src/components/Chat/ChatKitWidget.tsx
- [x] T028 [US4] Add "Listening..." and "Processing..." status text in frontend/src/components/Chat/VoiceInput.tsx

**Checkpoint**: Visual feedback complete for all voice states

---

## Phase 7: User Story 5 - Voice Error Handling and Recovery (Priority: P3)

**Goal**: Graceful error handling for voice recognition failures

**Independent Test**: Deny microphone permission, verify helpful error message shown

### Implementation for User Story 5

- [x] T029 [US5] Implement permission denied error handling in frontend/src/hooks/useVoiceInput.ts
- [x] T030 [US5] Implement no-speech timeout handling (10 seconds) in frontend/src/hooks/useVoiceInput.ts
- [x] T031 [US5] Implement speech recognition error recovery in frontend/src/hooks/useVoiceInput.ts
- [x] T032 [US5] Add fallback to Whisper API when Web Speech API unavailable in frontend/src/lib/voice-transcription.ts
- [x] T033 [US5] Implement MediaRecorder for audio capture (Whisper fallback) in frontend/src/lib/voice-transcription.ts
- [x] T034 [US5] Add cancel voice input functionality (click mic again or "cancel" command) in frontend/src/hooks/useVoiceInput.ts
- [x] T035 [US5] Display user-friendly error messages with recovery suggestions in frontend/src/components/Chat/VoiceIndicator.tsx
- [x] T036 [US5] Implement Whisper transcription endpoint logic in backend/app/routers/transcription.py
- [x] T037 [US5] Add file validation (format, size) to transcription endpoint in backend/app/routers/transcription.py

**Checkpoint**: Error handling complete - voice feature is robust

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements and quality improvements

- [x] T038 [P] Add voice feature export to frontend/src/components/Chat/index.ts
- [x] T039 [P] Update frontend/src/types/index.ts to export voice types
- [x] T040 Run quickstart.md test scenarios and document results
- [x] T041 Test on Chrome, Edge, Safari browsers and document compatibility
- [x] T042 [P] Add rate limiting to transcription endpoint (10 req/min) in backend/app/routers/transcription.py
- [x] T043 Verify text input still works alongside voice input

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| Phase 1: Setup | T001-T003 (3) | Types and configuration |
| Phase 2: Foundational | T004-T010 (7) | Core voice infrastructure |
| Phase 3: US1 - Task Creation | T011-T017 (7) | Voice task creation (P1) |
| Phase 4: US2 - Task Query | T018-T020 (3) | Voice task listing (P1) |
| Phase 5: US3 - Task Completion | T021-T022 (2) | Voice task completion (P2) |
| Phase 6: US4 - Visual Feedback | T023-T028 (6) | UI states and animations (P2) |
| Phase 7: US5 - Error Handling | T029-T037 (9) | Error recovery and fallback (P3) |
| Phase 8: Polish | T038-T043 (6) | Testing and refinements |
| **Total** | **43 tasks** | |

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3-7 (User Stories)**: Depend on Phase 2 completion
  - US1 and US2 are both P1 and can proceed in parallel after Phase 2
  - US3 and US4 are P2 and can proceed after Phase 2
  - US5 is P3 and handles the fallback path
- **Phase 8 (Polish)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (Task Creation)**: Depends on Phase 2 only - Core MVP
- **US2 (Task Query)**: Depends on Phase 2 only - Uses same voice infrastructure
- **US3 (Task Completion)**: Depends on Phase 2 only - Uses same voice infrastructure
- **US4 (Visual Feedback)**: Depends on Phase 2 only - Enhances all voice interactions
- **US5 (Error Handling)**: Depends on Phase 2 only - Provides fallback for US1-US4

### Parallel Opportunities

```
Phase 1:
  T001, T002, T003 can run in parallel (different files)

Phase 2:
  T006 (backend) can run in parallel with T004, T005 (frontend)
  T009, T010 can run in parallel (different components)

Phase 3 (US1):
  After T011-T013, T014-T017 can proceed

Phase 6 (US4):
  T023, T024, T025 can run in parallel (different states)

Phase 7 (US5):
  T029, T030, T031 can run in parallel (different error types)
  T036, T037 (backend) can run in parallel with frontend tasks

Phase 8:
  T038, T039 can run in parallel
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T010) - CRITICAL
3. Complete Phase 3: User Story 1 (T011-T017)
4. **STOP and VALIDATE**: Test voice task creation independently
5. Deploy/demo if ready - users can create tasks via voice!

### Incremental Delivery

1. Setup + Foundational → Voice infrastructure ready
2. Add US1 (Task Creation) → Test → Deploy (MVP!)
3. Add US2 (Task Query) → Test → Deploy
4. Add US4 (Visual Feedback) → Test → Deploy (Better UX)
5. Add US3 (Task Completion) → Test → Deploy
6. Add US5 (Error Handling) → Test → Deploy (Robust)
7. Polish phase → Final testing → Production ready

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [USn] label maps task to specific user story
- Web Speech API is primary, Whisper is fallback (US5)
- Existing ChatKitWidget handles AI processing - we only add voice input
- Audio is never persisted - privacy by design
- Test each user story independently before moving to next priority
