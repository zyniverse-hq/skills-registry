# Context-Specific Adaptations

Read this once the tech stack is detected in Phase 1, to tailor package choices, file
locations, and patterns to the project.

## For Laravel Projects (like SRMS)
- Use `razorpay/razorpay` composer package
- Create FormRequest for validation
- Use Jobs for async webhook processing
- Create API Resources for responses
- Follow existing auth patterns (Sanctum)
- Add to existing routes in `routes/api.php`

## For Next.js Projects
- Use `razorpay` npm package (server-side in API routes)
- Use React Hooks for checkout state management
- API routes in `app/api/` or `pages/api/`
- Use Server Actions (App Router) or API Routes (Pages Router)

## For React SPA
- Backend-agnostic frontend implementation
- Use Axios/Fetch for API calls
- Context API for order state management
- React Router for navigation flow

## For Express/Node.js
- Use `razorpay` npm package
- Middleware for signature validation
- Express routes for endpoints
- Use async/await for API calls
