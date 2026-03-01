# CLAUDE.md - KlyrSignals AI Instructions

## Project Overview

**KlyrSignals** is a portfolio analytics platform for Canadian investors, specifically designed to work with WealthSimple Trade exports.

**Current Version:** v1.5 (Dark Mode + WealthSimple Import)  
**Tech Stack:** Next.js 15, TypeScript, Tailwind CSS, FastAPI, Python  
**Repository:** https://github.com/humac/klyrsignals

---

## Architecture

### Frontend (`/frontend`)
- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS with dark mode support
- **State Management:** React Context (PortfolioContext, ThemeContext)
- **Charts:** Recharts
- **Deployment:** Vercel

### Backend (`/backend`)
- **Framework:** FastAPI
- **Language:** Python 3.12
- **API:** RESTful endpoints for portfolio analysis
- **Deployment:** Railway

---

## Key Features (v1.5)

### 1. Dark Mode
- Class-based theme toggle (`darkMode: 'class'` in tailwind.config.ts)
- System preference detection via `window.matchMedia`
- localStorage persistence (`klyrsignals_theme` key)
- ThemeContext provider wraps entire app
- ThemeToggle component in header (sun/moon icons)

**Files:**
- `frontend/context/ThemeContext.tsx` - Theme provider with system preference
- `frontend/components/ThemeToggle.tsx` - Toggle button component
- `frontend/tailwind.config.ts` - Dark mode configuration
- `frontend/app/globals.css` - Dark mode CSS variables

### 2. WealthSimple Import
- Auto-detection of WealthSimple CSV format
- Specialized parser handles BUY/SELL orders
- Commission included in cost basis
- Multiple purchases averaged (weighted average cost)
- Generic CSV fallback for other formats

**Files:**
- `frontend/lib/csv-parsers/wealthsimple.ts` - WealthSimple-specific parser
- `frontend/lib/csv-parsers/generic.ts` - Generic CSV parser
- `frontend/lib/csv-parsers/index.ts` - Auto-detection logic
- `frontend/app/import/page.tsx` - Import UI with format detection

---

## Development Workflow

### Local Development

```bash
# Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Start frontend (separate terminal)
cd frontend
npm run dev
```

### Build & Test

```bash
# Frontend build
cd frontend
npm run build
npm test

# Backend syntax check
cd backend
python -m py_compile app/main.py
```

### Important Commands

```bash
# Frontend
npm run dev          # Development server
npm run build        # Production build
npm run start        # Start production server
npm run lint         # ESLint check

# Backend
uvicorn app.main:app --reload  # Development server
pytest                         # Run tests (if configured)
```

---

## Code Style & Conventions

### TypeScript
- Use functional components with hooks
- Prefer `const` over `function` for component declarations
- Use TypeScript interfaces for type definitions
- Avoid `any` - use proper typing

```typescript
// ✅ Good
interface Holding {
  symbol: string;
  quantity: number;
  purchase_price: number;
  current_price: number;
}

const HoldingsTable: React.FC<{ holdings: Holding[] }> = ({ holdings }) => {
  // ...
};

// ❌ Avoid
const HoldingsTable = (props: any) => {
  // ...
};
```

### React Patterns
- Use `'use client'` directive for client components
- Context for global state (PortfolioContext, ThemeContext)
- Avoid prop drilling - use context or composition
- Memoize expensive computations with `useMemo`

### Tailwind CSS
- Use semantic color names (with dark mode support)
- Prefer utility classes over custom CSS
- Use responsive prefixes (`md:`, `lg:`)
- Dark mode with `dark:` prefix

```typescript
// ✅ Good
<div className="bg-white dark:bg-dark-surface text-gray-900 dark:text-dark-text">

// ❌ Avoid
<div className="bg-[#ffffff] dark:bg-[#0f172a]">
```

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints for function signatures
- Use Pydantic models for request/response validation
- Keep business logic in service layer, not routes

```python
# ✅ Good
from pydantic import BaseModel

class Holding(BaseModel):
    symbol: str
    quantity: float
    purchase_price: float

@app.post("/api/v1/analyze")
async def analyze_portfolio(holdings: list[Holding]) -> AnalysisResponse:
    # ...
```

---

## Testing Guidelines

### Frontend Tests
- Test user interactions (clicks, form submissions)
- Test theme toggle functionality
- Test CSV import flow end-to-end
- Verify localStorage persistence

### Backend Tests
- Test API endpoints with valid/invalid inputs
- Test edge cases (empty holdings, invalid symbols)
- Test error handling and status codes

---

## Common Tasks

### Adding a New Feature

1. **Update Requirements** (`docs/agent-workflow/REQ.md`)
   - Describe feature from user perspective
   - Define acceptance criteria

2. **Update Architecture** (`docs/agent-workflow/ARCH.md`)
   - Document component changes
   - Update data flow diagrams

3. **Implement** (create/modify files)
   - Follow existing patterns
   - Add tests
   - Update documentation

4. **Test** (manual + automated)
   - Run dev server
   - Test in browser
   - Verify build passes

5. **Document** (update guides)
   - USER_GUIDE.md for users
   - ADMIN_GUIDE.md for deployment

### Fixing a Bug

1. **Reproduce** the bug consistently
2. **Identify** root cause (check console, logs, code)
3. **Fix** with minimal changes
4. **Test** the fix thoroughly
5. **Document** in QA.md or ISSUES.md

---

## Known Issues & Gotchas

### Theme Flash on Reload
- **Issue:** Brief flash of wrong theme before localStorage loads
- **Solution:** ThemeContext uses `mounted` state to prevent SSR mismatch
- **Note:** `suppressHydrationWarning` on `<html>` tag is intentional

### Import State Persistence
- **Issue:** Holdings not persisting after import (v1.5 bug)
- **Fix:** Added `isInitialized` flag in PortfolioContext to prevent race condition
- **Location:** `frontend/context/PortfolioContext.tsx`

### CSV Parser Edge Cases
- **Issue:** Different CSV formats (WealthSimple vs generic)
- **Solution:** Auto-detection based on headers
- **Fallback:** Generic parser if format not recognized

---

## Deployment

### Frontend (Vercel)
1. Connect GitHub repository
2. Set build command: `npm run build`
3. Set output directory: `.next`
4. Environment variables (if any)

### Backend (Railway)
1. Connect GitHub repository
2. Set root directory: `backend`
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Environment variables:
   - `API_KEY` (if using external APIs)
   - `DATABASE_URL` (if using database in future)

---

## Project Structure

```
klyrsignals/
├── frontend/
│   ├── app/
│   │   ├── layout.tsx          # Root layout with providers
│   │   ├── page.tsx            # Dashboard
│   │   ├── import/
│   │   │   └── page.tsx        # Import page
│   │   ├── holdings/
│   │   │   └── page.tsx        # Holdings table
│   │   ├── analysis/
│   │   │   └── page.tsx        # Portfolio analysis
│   │   └── settings/
│   │       └── page.tsx        # Settings & export
│   ├── components/
│   │   ├── ThemeToggle.tsx     # Dark mode toggle
│   │   └── ...
│   ├── context/
│   │   ├── ThemeContext.tsx    # Theme provider
│   │   └── PortfolioContext.tsx # Portfolio state
│   ├── lib/
│   │   ├── csv-parsers/        # CSV import parsers
│   │   └── ...
│   └── public/
│       └── samples/            # Sample CSV files
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI app
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── health.py   # Health check endpoint
│   │   │       ├── mock.py     # Mock data endpoints
│   │   │       └── analysis.py # Portfolio analysis
│   │   └── models/
│   └── venv/                   # Python virtual environment
├── docs/
│   ├── agent-workflow/
│   │   ├── REQ.md              # Requirements
│   │   ├── ARCH.md             # Architecture
│   │   ├── TASKS.md            # Implementation tasks
│   │   ├── QA.md               # QA reports
│   │   ├── CLAUDE.md           # This file
│   │   └── GEMINI.md           # Gemini-specific instructions
│   ├── FINAL_REPORT.md         # Project closeout
│   └── RUN_STATE.md            # Pipeline state
└── agents/
    ├── tony.md                 # Architect persona
    ├── peter.md                # Developer persona
    ├── heimdall.md             # QA persona
    └── pepper.md               # Analyst persona
```

---

## Quick Reference

### Theme Toggle
```typescript
import { useTheme } from '@/context/ThemeContext';

const { theme, toggleTheme } = useTheme();
// theme: 'light' | 'dark'
// toggleTheme: () => void
```

### Portfolio Context
```typescript
import { usePortfolio } from '@/context/PortfolioContext';

const { holdings, importHoldings, clearPortfolio } = usePortfolio();
// holdings: Holding[]
// importHoldings: (newHoldings: Holding[]) => void
// clearPortfolio: () => void
```

### CSV Parsers
```typescript
import { detectCSVFormat, parseWealthSimpleCSV, parseGenericCSV } from '@/lib/csv-parsers';

const format = detectCSVFormat(headers); // 'wealthsimple' | 'generic'
const holdings = parseWealthSimpleCSV(csvText); // Holding[]
```

---

## Resources

- **Documentation:** `/docs` directory
- **Agent Files:** `/agents` directory
- **GitHub:** https://github.com/humac/klyrsignals
- **Issues:** Track in `docs/agent-workflow/ISSUES.md`

---

## When in Doubt

1. **Check existing code** - Follow established patterns
2. **Read ARCH.md** - Understand system design
3. **Check TASKS.md** - See implementation details
4. **Test in browser** - Verify changes work
5. **Ask for clarification** - Don't assume
