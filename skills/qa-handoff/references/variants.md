# Test-plan variant templates

The 10 variant templates the skill picks between in Step 4.5. **Load this file only when generating an issue body.** Each variant is a markdown template; Step 4.6 fills the `[bracketed placeholders]` with concrete PR-specific content (no `See the PR description` fallbacks — see SKILL.md's Step 4.6 banned-phrases list).

## Variant selection rules

Use the table in SKILL.md Step 4.5 to pick ONE variant. The chosen variant's template body replaces `<<VARIANT-TEMPLATE>>` in the outer template from Step 5.

For PRs hitting **multiple categories** (e.g., new feature that also touches auth): use the more user-visible variant (Variant 2 — New feature) and BORROW relevant sub-sections from the others (e.g., add a "Permission checks" sub-section from Variant 6).

## Variant 1 — Mechanical refactor

```markdown
## What to check

Nothing should LOOK different. Nothing should BREAK. Just confirm
the affected pages still work normally.

### Open these pages and check nothing is broken
- [ ] Sign in as [persona — admin/student/etc. based on affected routes]
      → go to [the affected page(s)]
- [ ] You should see [the page content], exactly like before
- [ ] [Any specific area touched] should load — no error, no blank space

### Quick sanity click-around (~2 minutes)
- [ ] Browse the affected module — nothing should look broken
- [ ] Log out, log back in → still works

**If anything blanks out, freezes, or shows an error message — that's a problem. Otherwise we're good.**
```

## Variant 2 — New feature

```markdown
## What to test

[1-line description of the new feature in plain English]

### As a [main user type]
- [ ] Sign in with [persona description, e.g. "an active premium plan"]
- [ ] Go to [page — describe how to get there, e.g. "Exams (left menu, or address bar /exams)"]
- [ ] You should see [the new visible element, e.g. "a banner at the top saying 'Predict my rank'"]
- [ ] Click [the new element] → [expected result]
- [ ] [Any follow-up action and expected result]

### As a [secondary user type — e.g. free user]
- [ ] Log out → sign in with [other persona]
- [ ] Go to the same [page]
- [ ] You should see [different/locked state]
- [ ] Click it → [expected result, e.g. "takes you to upgrade page"]
- [ ] You should NOT see [premium content]

### What should NOT change
- [ ] Rest of [the page] — list/search/filters/etc. — work like before
- [ ] On a phone, [the new element] fits nicely and doesn't overflow

**Problem = wrong content for wrong user type, click does nothing, or page breaks.**
```

## Variant 3 — Bug fix

> **Step 4.6 reminder:** Every `[bracketed placeholder]` below must be filled with PR-specific content derived from the PR body + diff. Generic phrases like *"the new, fixed behavior"* or *"reproduce the scenario in the PR"* are BANNED. Read the diff and describe the actual user-visible symptom.

```markdown
## What was broken (before this fix)

[1-2 line PLAIN-ENGLISH description of the user-visible symptom — e.g. "After submitting a test, pressing the browser back button kicked the user back into the test, losing their submitted answers" or "The dashboard showed a blank white screen for users on slow connections"]

## What to check (after this fix)

### Confirm the old bug is fixed
- [ ] [Specific reproduction steps — what URL, which persona, what action — e.g. "Sign in as a student, take any short test, submit it. On the results page, press the browser's back button."]
- [ ] **Expected:** [the SPECIFIC new behavior — e.g. "Stay on the results page; back button doesn't navigate anywhere"]
- [ ] **NOT expected:** [the SPECIFIC old symptom — e.g. "Navigates back into the test session with answers gone"]

### Confirm other scenarios still work
- [ ] [Specific normal case — e.g. "Forward navigation from results to dashboard still works"]
- [ ] [Specific adjacent case — e.g. "Refreshing the results page still shows the results"]

**Bug = [restate the specific old symptom]. Otherwise we're good.**
```

## Variant 4 — UI / styling

```markdown
## What to look at

[1-line description — e.g. "The exam cards on the Dashboard got a new look"]

### Look at it
- [ ] Open the [page] after sign-in
- [ ] Look at [the changed element]
- [ ] It should look [cleaner / better spaced / easier to read]
- [ ] Compare with the design [Figma link if available] → should match

### Try it on different screens
- [ ] **Desktop / laptop** — [expected layout, e.g. "neat grid, evenly spaced"]
- [ ] **Tablet (iPad-size)** — [expected adaptation, e.g. "fewer columns, still neat"]
- [ ] **Mobile / phone** — [expected, e.g. "stacks one per row, text readable, not squished"]

### Make sure it still WORKS
- [ ] Click [the element] → [original behavior preserved]
- [ ] On desktop, hover → [highlight/animation still happens]

**Problems = looks broken on any screen size, text cut off, elements overlap, or clicking does nothing.**
```

## Variant 5 — Performance / data

> **Note for the skill:** the outer template already has a `## What changed` section that gets filled with a 1–2 line plain-English summary. This variant starts directly at `## What to check` — do NOT add another `## What changed` heading here. If the outer summary needs to mention "should be faster" framing, include it in the outer `## What changed` directly.

```markdown
## What to check

### Speed (is it faster?)
- [ ] Open [the affected page] → should load in **under [target] seconds**
- [ ] Open [the same page] for **5 different items** in a row — all snappy

### Correctness (most important — is the data right?)
- [ ] Pick [a known item — e.g. "a student whose score/answers you remember"]
- [ ] Open [their data] → should be **exactly the same** as before
- [ ] Spot-check [2-3 specific data points] — same as before

### Edge cases
- [ ] [Item with lots of data] → still fast, all visible
- [ ] [Item with very little data] → still fast, what's there is visible

**Problems = data looks different/wrong, page takes more than [threshold], or some content missing.**
```

## Variant 6 — Permission / access control

```markdown
## What to check

This change adjusts WHO can access [the feature/page]. Verify each
user type sees the right thing.

### As a paid (premium) user
- [ ] Sign in with an active **premium** plan
- [ ] Go to [page]
- [ ] You SHOULD see [the protected content]

### As a free user
- [ ] Log out → sign in with a **free** user
- [ ] Go to the same [page]
- [ ] You should see [the locked state / upgrade message]
- [ ] You should NOT see [the premium content]
- [ ] Clicking the locked area → [opens upgrade page, NOT a crash]

### As an admin user (if applicable)
- [ ] Log out → sign in as **admin**
- [ ] You SHOULD have full access

### As a logged-out visitor (if applicable)
- [ ] Open the URL in an incognito/private window
- [ ] You should be sent to login — NOT see the protected content

**Problem = wrong user sees protected content, or correct user gets locked out.**
```

## Variant 7 — Multi-tenant / B2B vs B2C

```markdown
## What to check

This change behaves differently on B2C vs B2B accounts. Verify both.

### B2C — public <your-domain>
- [ ] Open https://<dev-url>
- [ ] Sign in with a **B2C** user
- [ ] [Expected behavior in B2C — e.g. "Academic menu should NOT appear"]

### B2B — organization-specific URL
- [ ] Open the B2B tenant URL — e.g. https://<tenant>.<your-domain>
- [ ] Sign in with a **B2B user from that organization**
- [ ] [Expected behavior in B2B — e.g. "Academic menu appears with the org's syllabus"]

### Cross-org isolation (very important)
- [ ] As a B2B user from org A, you should NOT see any content
      belonging to org B (no data leakage)
- [ ] The org name and logo at the top should match the tenant you're on

**Problem = wrong content for wrong tenant, org data leaking, or feature appearing where it shouldn't.**
```

## Variant 8 — External integration

```markdown
## What to check

This change updates how we connect to [Razorpay / Deepgram / OpenAI / ElevenLabs / Sentry].
Test the full flow end-to-end.

### The main flow works
- [ ] Sign in → go to [the page/feature that uses this integration]
- [ ] Trigger the action — for this integration:
      - **Razorpay:** Click "Pay" / "Upgrade" → Razorpay popup appears
        → complete a test payment
      - **Deepgram:** Click "Start voice interview" → microphone activates
        → your speech turns into text on screen
      - **OpenAI:** Click "Generate practice question" → a sensible
        question appears in a few seconds (not gibberish, not blank)
      - **ElevenLabs:** Voice playback works in mock interview
      - **Sentry:** Hit an error path → no extra crash for the user
- [ ] After completion, you return to the app and see the success state

### When the third party is slow or fails
- [ ] If it takes long, you should see a loading spinner — NOT a frozen page
- [ ] If it fails (cancel the Razorpay popup, or stop voice mid-flow),
      you should see a friendly error — NOT a crash

### Record-keeping
- [ ] After success, the action shows in your history / transactions /
      session list (wherever that lives in the app)

**Problem = third-party doesn't open, takes forever, or app crashes when it fails.**
```

## Variant 9 — Onboarding / first-time-user

```markdown
## What to check

This change updates the new-user onboarding (welcome / tutorial / first-time setup).

### Sign up as a brand-new user
- [ ] Use an email you haven't used before (e.g. test+<timestamp>@example.com)
- [ ] Complete the signup flow
- [ ] Expected: you see [welcome screen / tutorial / first-time setup]
- [ ] Walk through it → you land on [dashboard / specific page]

### Skip or dismiss the onboarding
- [ ] Sign up with another new email
- [ ] If there's a "Skip" or "Dismiss" button, click it
- [ ] Expected: you land on [default page] without errors

### Existing users (very important)
- [ ] Log out → log in as an EXISTING user (one who's signed in before)
- [ ] Expected: you do NOT see the onboarding again
- [ ] You land where you normally land (dashboard / last page)

**Problem = new users don't see onboarding, existing users see it again, or the skip button breaks the flow.**
```

## Variant 10 — Content / copy / translation

```markdown
## What to check

This change updates the wording / labels on [page/feature].

### Check the new wording in context
- [ ] Go to [page]
- [ ] The text on [button / label / heading] should now read:
      "[exact new text]"
- [ ] The wording makes sense — not awkward, not cut off, not weird in context

### Different screen sizes
- [ ] On mobile, the text fits and reads clearly (no truncation with "...")
- [ ] On smaller buttons, the new text doesn't overflow

### Other languages (if multilingual)
- [ ] Switch the language toggle to [Hindi / other supported]
- [ ] The translated version of the new text appears (or a sensible fallback)

**Problem = old text still showing in places, new text cut off, looks awkward, or missing translation.**
```

## Style rules (apply to ALL variants)

- **No code references** — no file paths, no component names, no `useFoo`, no console references
- **Concrete personas** — "Sign in as admin / free user / premium user" instead of "authenticated user with role X"
- **Concrete actions** — "Click the banner" instead of "trigger the modal"
- **Expected vs NOT expected** — clear pass/fail signal in plain words
- **Bold key UI labels** — "**Exams** menu", "**Predict my rank** banner" — helps QA find them
- **Time estimates** — "~2 minutes sanity check" — sets expectation
- **One closing line in bold** — explicit definition of "problem" at the end
