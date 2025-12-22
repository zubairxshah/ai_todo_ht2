# Tasks: Voice UX Enhancements

**Input**: Design documents from `/specs/002-voice-ux-enhancements/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Manual testing required for voice functionality (Web Speech API requires browser). No automated tests for this feature.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No setup required - project already initialized with Next.js, TypeScript, and voice input components.

- [x] T001 Verify existing project structure matches plan.md

**Checkpoint**: Setup complete - feature branches and project structure ready

---

## Phase 2: User Story 1 - Auto-Execute Voice Commands (Priority: P1) 🎯 MVP

**Goal**: Voice commands execute immediately without populating text input field

**Independent Test**: Click mic, speak "Add task buy milk", verify task created without text appearing in input field

### Implementation for User Story 1

- [x] T002 [US1] Extract submission logic from handleSubmit into reusable submitMessage function in frontend/src/components/Chat/ChatKitWidget.tsx
- [x] T003 [US1] Modify handleVoiceTranscription to call submitMessage directly without setInput in frontend/src/components/Chat/ChatKitWidget.tsx
- [x] T004 [US1] Remove the 500ms setTimeout delay for voice submission in frontend/src/components/Chat/ChatKitWidget.tsx
- [x] T005 [US1] Add empty string check for voice transcription before submission in frontend/src/components/Chat/ChatKitWidget.tsx
- [x] T006 [US1] Manual test: Verify voice commands execute without populating input field (code review passed, build succeeds)

**Checkpoint**: Voice commands now execute directly without showing text in input field

---

## Phase 3: User Story 2 - Application Favicon (Priority: P1)

**Goal**: Custom favicon visible in browser tab for app identification

**Independent Test**: Open app in browser, verify custom icon in tab

### Implementation for User Story 2

- [x] T007 [P] [US2] Download favicon from https://cdn-icons-png.freepik.com/512/17394/17394786.png to frontend/src/app/icon.png
- [x] T008 [US2] Verify favicon file is valid PNG format and properly sized (512x512 PNG verified)
- [ ] T009 [US2] Manual test: Verify favicon displays in browser tab after page refresh

**Checkpoint**: Favicon visible in browser tab and bookmarks

---

## Phase 4: User Story 3 - Deployment Verification (Priority: P2)

**Goal**: All code changes pushed to GitHub and Vercel deployment verified

**Independent Test**: Access production URL and verify app loads with new features

### Implementation for User Story 3

- [x] T010 [US3] Check git status for uncommitted changes
- [x] T011 [US3] Stage and commit all changes with descriptive commit message
- [x] T012 [US3] Push changes to remote repository (origin)
- [ ] T013 [US3] Verify Vercel deployment triggered and succeeds (user to verify)
- [ ] T014 [US3] Manual test: Access production URL and verify favicon + voice work (user to verify)

**Checkpoint**: All changes deployed and verified in production

---

## Phase 5: Polish & Validation

**Purpose**: Final validation and cleanup

- [ ] T015 Manual test: Verify text input still works normally (regression test)
- [ ] T016 Update Definition of Done checklist in plan.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - verification only
- **Phase 2 (US1 - Voice)**: Sequential within phase (T002 → T003 → T004 → T005 → T006)
- **Phase 3 (US2 - Favicon)**: Independent of Phase 2, can run in parallel
- **Phase 4 (US3 - Deploy)**: Depends on Phase 2 and Phase 3 completion
- **Phase 5 (Polish)**: Depends on Phase 4 completion

### Parallel Opportunities

- T007 (favicon download) can run in parallel with T002-T005 (voice changes)
- Different user stories can be worked on in parallel

### Within User Story 1

- T002 must complete before T003 (extracting function before using it)
- T003 must complete before T004 (modifying callback before removing delay)
- T004 and T005 can run in parallel (different concerns)
- T006 depends on all prior tasks

---

## Notes

- No automated tests for voice functionality (requires browser with Web Speech API)
- Favicon uses Next.js file convention (auto-detected in app/ directory)
- Manual testing required for voice and favicon verification
- Git operations require user to have push access to remote repository
