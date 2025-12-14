# Frontend - Claude Code Rules

## Project Context

This is a Next.js 14 frontend application using App Router, TypeScript, and Tailwind CSS.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth client

## Directory Structure

```
frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   │   ├── dashboard/    # Main task management page
│   │   ├── login/        # Login page
│   │   └── register/     # Registration page
│   ├── components/       # Reusable React components
│   ├── lib/              # Utilities, API client, auth config
│   └── types/            # TypeScript type definitions
├── public/               # Static assets
└── package.json
```

## Code Standards

### TypeScript

- Use strict TypeScript configuration
- Define interfaces for all props and API responses
- Avoid `any` type; use `unknown` when type is uncertain
- Use type inference where possible

### React/Next.js

- Use functional components with hooks
- Prefer Server Components where possible
- Use `'use client'` directive only when necessary
- Follow Next.js App Router conventions

### Styling

- Use Tailwind CSS utility classes
- Avoid inline styles
- Use consistent spacing and color tokens
- Mobile-first responsive design

### API Communication

- Use fetch with proper error handling
- Always include Authorization header for protected routes
- Handle loading and error states in UI
- Type all API responses

## Environment Variables

Required in `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=<shared-secret>
NEXT_PUBLIC_AUTH_URL=http://localhost:3000
```

## Commands

```bash
npm run dev      # Start development server (port 3000)
npm run build    # Production build
npm run start    # Start production server
npm run lint     # Run ESLint
```

## Key Files

- `src/lib/auth.ts` - Better Auth configuration
- `src/lib/api.ts` - API client for backend communication
- `src/app/layout.tsx` - Root layout with providers
- `src/app/dashboard/page.tsx` - Main task management UI

## Testing

- Test components with React Testing Library
- Test hooks with renderHook
- Mock API calls in tests

## Security

- Never expose secrets in client-side code
- Use `NEXT_PUBLIC_` prefix only for safe-to-expose values
- Validate user input before sending to API
- Handle auth errors gracefully (redirect to login)
