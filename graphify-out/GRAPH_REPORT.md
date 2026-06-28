# Graph Report - Hospital_Managment  (2026-06-26)

## Corpus Check
- 24 files · ~10,319 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 124 nodes · 127 edges · 23 communities (14 shown, 9 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 19 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8a8db087`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]

## God Nodes (most connected - your core abstractions)
1. `GoogleCredentials` - 8 edges
2. `🎙️ Script & Action Guide` - 8 edges
3. `UserProfile` - 7 edges
4. `AvailabilitySlot` - 7 edges
5. `Booking` - 7 edges
6. `BookingRaceConditionTest` - 7 edges
7. `Setup and Run` - 7 edges
8. `UserProfileAdmin` - 5 edges
9. `AvailabilitySlotAdmin` - 5 edges
10. `BookingAdmin` - 5 edges

## Surprising Connections (you probably didn't know these)
- `UserProfileAdmin` --uses--> `AvailabilitySlot`  [INFERRED]
  hms/core/admin.py → hms/core/models.py
- `UserProfileAdmin` --uses--> `Booking`  [INFERRED]
  hms/core/admin.py → hms/core/models.py
- `UserProfileAdmin` --uses--> `GoogleCredentials`  [INFERRED]
  hms/core/admin.py → hms/core/models.py
- `UserProfileAdmin` --uses--> `UserProfile`  [INFERRED]
  hms/core/admin.py → hms/core/models.py
- `AvailabilitySlotAdmin` --uses--> `AvailabilitySlot`  [INFERRED]
  hms/core/admin.py → hms/core/models.py

## Import Cycles
- None detected.

## Communities (23 total, 9 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.15
Nodes (13): AvailabilitySlotAdmin, BookingAdmin, GoogleCredentialsAdmin, UserProfileAdmin, AvailabilitySlot, Booking, GoogleCredentials, Meta (+5 more)

### Community 1 - "Community 1"
Cohesion: 0.17
Nodes (7): create_google_calendar_event(), get_google_oauth_flow(), google_auth_callback(), google_auth_redirect(), process_booking_background(), signup_view(), trigger_email_notification()

### Community 2 - "Community 2"
Cohesion: 0.13
Nodes (14): 1. Workspace Configuration, 2. Initialize Database, 3. Start Local Mock SMTP Server (Terminal 1), 4. Start Serverless Email Service (Terminal 2), 5. Run Django Application (Terminal 3), Data Model Decisions, Django App & Serverless Connection, Google Calendar Integration (+6 more)

### Community 3 - "Community 3"
Cohesion: 0.17
Nodes (11): 💡 Quick Tips for Recording, 🎙️ Script & Action Guide, Section 1: Project Overview & Tech Stack (0:00 - 1:00), Section 2: Doctor Flow (1:00 - 2:30), Section 3: Patient Flow (2:30 - 4:30), Section 4: Slot Blocking & Race Condition Verification (4:30 - 5:30), Section 5: Email Notifications (5:30 - 7:00), Section 6: Google Calendar OAuth Integration (7:00 - 8:30) (+3 more)

### Community 4 - "Community 4"
Cohesion: 0.25
Nodes (7): description, devDependencies, serverless-offline, name, scripts, start, version

### Community 5 - "Community 5"
Cohesion: 0.29
Nodes (6): AI Tool Usage Log, Prompt 1: Initial Requirement Analysis, Prompt 2: Execution Start, Prompt 3: Healthcare Redesign & AI Assistant Makeover, Session Information, Thread Summary

### Community 6 - "Community 6"
Cohesion: 0.29
Nodes (3): BaseHTTPRequestHandler, EmailHandler, Standalone Email Service for Mini HMS. Replaces the Serverless offline endpoint

### Community 7 - "Community 7"
Cohesion: 0.33
Nodes (6): Named Problem: Handling Concurrent Slot Booking Race Conditions, Option A: Application-Level Verification, Option B: Database-Level Row Locking via Transactions (`select_for_update`), Options Considered, Selected Choice and Defense: Option B, The Design Decision

## Knowledge Gaps
- **37 isolated node(s):** `name`, `version`, `description`, `start`, `serverless-offline` (+32 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Mini Hospital Management System (HMS)` connect `Community 2` to `Community 7`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `GoogleCredentials` (e.g. with `AvailabilitySlotAdmin` and `BookingAdmin`) actually correct?**
  _`GoogleCredentials` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `UserProfile` (e.g. with `AvailabilitySlotAdmin` and `BookingAdmin`) actually correct?**
  _`UserProfile` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `AvailabilitySlot` (e.g. with `AvailabilitySlotAdmin` and `BookingAdmin`) actually correct?**
  _`AvailabilitySlot` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `Booking` (e.g. with `AvailabilitySlotAdmin` and `BookingAdmin`) actually correct?**
  _`Booking` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `version`, `description` to the rest of the system?**
  _45 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._