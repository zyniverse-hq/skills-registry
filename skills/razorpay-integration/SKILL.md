---
name: razorpay-integration
description: Integrate Razorpay payment gateway end-to-end. Activate when users mention Razorpay, payment gateway, checkout, order creation, payment verification, webhook handling, or switching to live keys.
allowed-tools: Read Glob Grep Write Edit Bash AskUserQuestion EnterPlanMode ExitPlanMode TaskCreate TaskUpdate TaskList
metadata:
  version: 1.1.0
  author: Tazeen Soudagar
  email: tazeen.soudagar@zysk.tech
  category: engineering-practice
  tags:
    - razorpay
    - payment-gateway
    - payments
    - checkout
    - webhooks
  product: zysk
  sprint: 1
  tested_with: claude-sonnet-4-6
  user-invocable: true
---

# Razorpay Payment Gateway Integration

> Guide users through a complete Razorpay integration — from tech stack discovery and plan approval to backend order creation, payment verification, and webhook handling.

## When to use

- Activate when: the user mentions Razorpay, payment gateway, or checkout flow
- Activate when: the user wants to integrate payments or accept money in their app
- Activate when: the user asks about order creation, payment verification, or webhook handling
- Activate when: the user wants to switch from Razorpay test keys to live keys
- Do NOT activate when: the user is asking about a different payment provider (Stripe, PayPal, PayU) — those require different SDKs and flows

## Prerequisites

- [ ] A Razorpay account — test mode is free and sufficient to start
- [ ] Test API credentials: `key_id` and `key_secret` from the Razorpay dashboard
- [ ] Access to both backend and frontend of the project codebase
- [ ] Database access to create orders and payments tables
- [ ] HTTPS configured in production (Razorpay requires it for live keys)

## Steps

This skill runs in three phases: discovery, planning, and implementation. Do not write any code until the user explicitly approves the plan at the end of Phase 2.

### Phase 1: Project Analysis & Discovery

#### Step 1: Detect Tech Stack

Analyze the codebase to identify:
- **Backend framework**: Laravel, Node.js, Express, NestJS, Django, Flask, etc.
- **Frontend framework**: React, Next.js, Vue, Angular, vanilla JS
- **Database**: MySQL, PostgreSQL, MongoDB, etc.
- **Existing auth system**: Session-based, JWT, Sanctum, Passport
- **API pattern**: REST, GraphQL
- **Project type**: E-commerce, SaaS, booking system, service marketplace

Use Glob and Read tools to examine:
- `package.json`, `composer.json`, `requirements.txt`
- Config files: `vite.config.*`, `next.config.*`, `config/*.php`
- Route files, API endpoints
- Database models/schemas

#### Step 2: Understand Business Flow

Ask the user context-specific questions using AskUserQuestion:
- What triggers payment? (Cart checkout, service booking, subscription, one-time purchase)
- What user data is available at checkout? (Email, phone, address)
- Are there multiple payment amounts or packages?
- Do you need recurring payments/subscriptions?
- Should payment success trigger specific actions? (Order fulfillment, service activation, notifications)
- Do you have test/staging environments?

### Phase 2: Technical Roadmap Creation

#### Step 3: Generate Visual Payment Flow

Read `references/payment-flow.md` for the full ASCII diagram. Customize the labels to match the user's actual use case — their specific flow triggers, endpoint paths, and post-payment business actions — then share it with the user.

#### Step 4: Create Detailed Technical Plan

Present a structured implementation plan in markdown format:

**A. Backend Setup**
- Install Razorpay SDK (specific to detected framework)
- Configure environment variables (keys, webhook secret)
- Create database schema for orders, payments, transactions
- Implement Order Creation endpoint
- Implement Payment Verification endpoint
- Implement Webhook handler endpoint
- Add signature validation helper
- Create payment-related migrations

**B. Frontend Setup**
- Add Razorpay Checkout.js script
- Create checkout page/component
- Implement payment initialization logic
- Handle success/failure callbacks
- Add loading states and error handling
- Create order confirmation page

**C. Security Measures**
- Never expose key_secret to frontend (server-side only)
- Validate all webhook signatures
- Use HTTPS in production
- Implement CSRF protection on payment endpoints
- Store sensitive data encrypted
- Log all payment transactions for audit

**D. Testing Strategy**
- Use Razorpay test mode credentials
- Test cards: 4111 1111 1111 1111 (success), 4000 0000 0000 0002 (failure)
- Test UPI: success@razorpay
- Test webhook events with Razorpay dashboard
- Verify signature validation logic
- Test failure scenarios (network errors, timeout, invalid signature)

**E. Production Checklist**
- Replace test keys with live keys
- Enable webhook subscriptions in Razorpay dashboard
- Set up proper error monitoring
- Configure payment failure notifications
- Add transaction receipts/invoices
- Implement refund handling (if needed)
- Set up customer support flow for payment issues

#### Step 5: Present for Approval

Create a summary document showing:
1. **Detected Configuration**: Framework versions, auth system, existing patterns
2. **Proposed Architecture**: Files to create/modify with rationale
3. **Data Flow Diagram**: The ASCII diagram above customized to their use case
4. **Implementation Timeline**: Ordered task list
5. **Open Questions**: Any clarifications needed before proceeding

Get explicit sign-off from the user before writing any code. Payment integrations touch databases, environment config, and real money — misaligned assumptions are expensive to unwind.

Ask user:
```
I've prepared a Razorpay integration plan tailored to your {PROJECT_TYPE} project.

Summary:
- Backend: {FRAMEWORK}
- Frontend: {FRAMEWORK}
- Payment trigger: {BUSINESS_FLOW}
- Estimated files to create: {COUNT}
- Estimated files to modify: {COUNT}

Please review the detailed flow diagram and technical plan above.

Would you like to:
1. Approve and proceed with implementation
2. Request modifications to the plan
3. Ask questions about specific steps
```

### Phase 3: Implementation (Only After Approval)

#### Step 6: Execute Implementation

Use TaskCreate to break down implementation into discrete tasks:

1. **Backend: Environment Configuration**
   - Add RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, RAZORPAY_WEBHOOK_SECRET to .env
   - Update config files

2. **Backend: Database Schema**
   - Create orders table (id, user_id, razorpay_order_id, amount, currency, status, created_at)
   - Create payments table (id, order_id, razorpay_payment_id, method, status, verified_at)
   - Run migrations

3. **Backend: SDK Integration**
   - Install Razorpay SDK via package manager
   - Create Razorpay service/helper class

4. **Backend: Create Order Endpoint**
   - Route + Controller for POST /api/orders/create
   - Validate request, call Razorpay API, store order

5. **Backend: Payment Verification Endpoint**
   - Route + Controller for POST /api/payments/verify
   - Signature validation logic
   - Update order status, trigger fulfillment

6. **Backend: Webhook Handler**
   - Route for POST /api/webhooks/razorpay
   - Signature validation
   - Event processing (payment.captured, payment.failed, etc.)

7. **Frontend: Checkout Component**
   - Add Razorpay script to HTML/layout
   - Create checkout page with payment button
   - Initialize Razorpay with order details

8. **Frontend: Payment Handler**
   - Success callback implementation
   - Failure handler
   - Redirect logic

9. **Frontend: Order Confirmation Page**
   - Display order details
   - Show payment status
   - Download invoice/receipt option

10. **Testing & Verification**
    - Test with test credentials
    - Verify all failure paths
    - Test webhook locally (ngrok or similar)

Mark each task as completed after implementation and verification.

#### Step 7: Post-Implementation Guide

After implementation is complete, provide:
- **Testing checklist**: Step-by-step test scenarios
- **Going live guide**: Switching from test to live mode
- **Monitoring setup**: What to track (failed payments, signature mismatches)
- **Common issues**: Troubleshooting guide for typical problems
- **Next steps**: Optional enhancements (subscriptions, EMI, international payments)

## Output

- **Format:** Implementation delivered as real code files, plus a final summary message in chat
- **Location:** Files written directly into the project codebase at paths agreed in the plan; summary appears inline in chat
- **Contents of the final summary:**
  - List of all files created or modified (with paths)
  - Environment variables to configure
  - Step-by-step testing instructions using test credentials
  - Production deployment checklist (switching to live keys, webhook setup)

## Example

**User says:** "I want to add Razorpay payment to my Laravel + React app."

**Claude does:** Scans `composer.json`, route files, and models to detect the stack; asks 5–6 targeted questions about the business flow; generates a customized payment-flow diagram; presents a file-by-file implementation plan for approval; then — after the user approves — creates the orders/payments migrations, a RazorpayService class, two API controllers (order creation + payment verification), a webhook route with signature validation, and a React checkout component.

**Result:** A working end-to-end payment flow: the user can create an order, complete payment in the Razorpay checkout modal, and see the order marked as paid in the database — verified with a test card before going live.

## Context-Specific Adaptations

Framework-specific integration notes (Laravel/Forge, Next.js, React SPA, Express/Node) live in
`references/framework-adaptations.md`. Read it once the tech stack is detected in Phase 1 to
tailor package choices, file locations, and patterns to the project.

## Important Conventions

1. **Always use environment variables** for keys - never hardcode
2. **Amounts are in paise** (multiply by 100): ₹100 = 10000 paise
3. **Currency code**: "INR" for Indian Rupees
4. **Order IDs must be unique** per merchant
5. **Signatures are HMAC SHA256** - use proper crypto libraries
6. **Webhooks are async** - don't rely on them for immediate confirmation
7. **Test mode vs Live mode** - completely separate keys and dashboards

## Skill Completion

The skill is considered complete when:
1. Payment flow is documented and approved
2. Backend order creation works
3. Payment verification with signature validation works
4. Webhook handler is implemented
5. Frontend checkout flow is functional
6. Test payment succeeds end-to-end
7. User can demonstrate a complete payment cycle

## Notes

- HTTPS is mandatory for Razorpay live keys — flag this early if the project isn't already set up for it
- For projects with existing data, recommend a database backup before running schema migrations
- Webhooks are asynchronous; do not rely on them for the immediate post-payment redirect — use the frontend callback for that, and webhooks for reconciliation
- Razorpay test mode and live mode use completely separate key pairs and dashboards — switching is a two-step change (env vars + dashboard webhook URL)
- Payment failures are user-facing; graceful error messages and retry flows matter as much as the happy path
- `ngrok` or a similar tunnel is required to test webhooks locally — flag this during planning
