# Razorpay Payment Flow Diagram

Customize the labels below to match the user's actual use case — their flow triggers, endpoint paths, and business actions after payment.

```
┌─────────────────────────────────────────────────────────────┐
│                    RAZORPAY PAYMENT FLOW                     │
└─────────────────────────────────────────────────────────────┘

FRONTEND (User Journey)
─────────────────────────
[1] User Action (e.g., Add to Cart, Click "Checkout")
        │
        ├─> Collect user details (name, email, phone)
        │
        ▼
[2] POST to Backend: Create Order Request
        │
        └─> Payload: { amount, currency, items/service_id, user_info }

BACKEND (Order Creation)
────────────────────────
[3] Receive order request
        │
        ├─> Validate user session/auth
        ├─> Calculate total amount (apply discounts/taxes)
        ├─> Create order record in DB (status: "pending")
        │
        ▼
[4] Call Razorpay Orders API
        │
        ├─> POST https://api.razorpay.com/v1/orders
        ├─> Auth: Basic (key_id:key_secret)
        ├─> Body: { amount (paise), currency: "INR", receipt, notes }
        │
        ▼
[5] Receive Razorpay order_id
        │
        ├─> Store order_id with order record
        └─> Return to frontend: { order_id, amount, key_id }

FRONTEND (Checkout Initialization)
──────────────────────────────────
[6] Load Razorpay Checkout.js SDK
        │
        ▼
[7] Initialize Razorpay instance
        │
        ├─> key: RAZORPAY_KEY_ID
        ├─> amount: order.amount
        ├─> order_id: order.order_id
        ├─> prefill: { name, email, contact }
        ├─> handler: onPaymentSuccess callback
        │
        ▼
[8] Open Razorpay payment modal
        │
        └─> User selects payment method (UPI, Card, Netbanking, Wallet)

RAZORPAY (Payment Processing)
──────────────────────────────
[9] Process payment
        │
        ├─> 3D Secure authentication (if card)
        ├─> Bank authorization
        │
        ▼
[10] Payment Success/Failure
        │
        └─> Return payment_id + signature (if success)

FRONTEND (Post-Payment)
───────────────────────
[11] Razorpay handler callback triggered
        │
        ├─> Receive: { razorpay_order_id, razorpay_payment_id, razorpay_signature }
        │
        ▼
[12] POST to Backend: Verify Payment
        │
        └─> Payload: { order_id, payment_id, signature }

BACKEND (Verification & Fulfillment)
────────────────────────────────────
[13] Receive verification request
        │
        ├─> Generate expected signature:
        │   hmac_sha256(order_id + "|" + payment_id, key_secret)
        │
        ├─> Compare with received signature
        │
        ▼
[14] If signature valid:
        │
        ├─> Update order status: "paid"
        ├─> Store payment_id, payment_method, paid_at timestamp
        ├─> Trigger business logic:
        │   • Send confirmation email
        │   • Create invoice
        │   • Activate service/subscription
        │   • Update inventory (if e-commerce)
        │   • Notify admins/vendors
        │
        └─> Return success response to frontend

[15] If signature invalid:
        │
        ├─> Log security event
        ├─> Mark order as "verification_failed"
        └─> Return error response

FRONTEND (Completion)
─────────────────────
[16] Redirect user based on verification result
        │
        ├─> Success: /order-confirmation?id={order_id}
        └─> Failure: /payment-failed?id={order_id}

WEBHOOK (Async Verification - Optional but Recommended)
────────────────────────────────────────────────────────
[W1] Razorpay sends webhook to your server
        │
        ├─> POST https://yourdomain.com/api/webhooks/razorpay
        ├─> Event: payment.captured, payment.failed, refund.created, etc.
        │
        ▼
[W2] Validate webhook signature
        │
        ├─> X-Razorpay-Signature header
        ├─> Compare with hmac_sha256(webhook_body, webhook_secret)
        │
        ▼
[W3] Process event
        │
        ├─> Update payment status
        ├─> Handle edge cases (delayed capture, partial refunds)
        └─> Send notifications
```
