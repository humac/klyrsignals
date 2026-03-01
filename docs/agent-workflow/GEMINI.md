# GEMINI.md - KlyrSignals AI Instructions

## Project Overview

**KlyrSignals** is a portfolio analytics platform for Canadian investors, specifically designed to work with WealthSimple Trade exports.

**Current Version:** v1.5 (Dark Mode + WealthSimple Import)  
**Tech Stack:** Next.js 15, TypeScript, Tailwind CSS, FastAPI, Python  
**Repository:** https://github.com/humac/klyrsignals

---

## Quick Start

### Local Development

```bash
# Terminal 1: Backend
cd /home/openclaw/.openclaw/workspace/jarvis/projects/klyrsignals/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend
cd /home/openclaw/.openclaw/workspace/jarvis/projects/klyrsignals/frontend
npm run dev
```

**Access:** http://localhost:3000

---

## Architecture Summary

### Frontend
- **Next.js 15** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** with dark mode (`darkMode: 'class'`)
- **React Context** for state (PortfolioContext, ThemeContext)
- **Recharts** for data visualization

### Backend
- **FastAPI** for REST API
- **Python 3.12**
- **Pydantic** for data validation
- **Uvicorn** ASGI server

---

## v1.5 Features

### 1. Dark Mode ✅

**Implementation:**
- ThemeContext with localStorage + system preference detection
- ThemeToggle component (sun/moon icons)
- All 5 pages styled with `dark:` Tailwind classes
- Color palette: slate-based dark theme

**Key Files:**
- `frontend/context/ThemeContext.tsx`
- `frontend/components/ThemeToggle.tsx`
- `frontend/tailwind.config.ts`
- `frontend/app/globals.css`

**Usage:**
```typescript
import { useTheme } from '@/context/ThemeContext';

const { theme, toggleTheme } = useTheme();
// theme = 'light' | 'dark'
```

### 2. WealthSimple Import ✅

**Implementation:**
- Auto-detection of CSV format based on headers
- Specialized parser for WealthSimple Trade confirmations
- Handles BUY/SELL orders
- Includes commission in cost basis
- Averages multiple purchases of same symbol

**Key Files:**
- `frontend/lib/csv-parsers/wealthsimple.ts`
- `frontend/lib/csv-parsers/generic.ts`
- `frontend/lib/csv-parsers/index.ts`
- `frontend/app/import/page.tsx`

**Usage:**
```typescript
import { detectCSVFormat, parseWealthSimpleCSV } from '@/lib/csv-parsers';

const format = detectCSVFormat(headers); // 'wealthsimple' | 'generic'
const holdings = parseWealthSimpleCSV(csvText); // Holding[]
```

---

## File Structure

```
klyrsignals/
├── frontend/
│   ├── app/
│   │   ├── layout.tsx          # Root layout (ThemeProvider + PortfolioProvider)
│   │   ├── page.tsx            # Dashboard (portfolio summary)
│   │   ├── import/
│   │   │   └── page.tsx        # CSV import with auto-detection
│   │   ├── holdings/
│   │   │   └── page.tsx        # Holdings table
│   │   ├── analysis/
│   │   │   └── page.tsx        # Portfolio analysis & risk scoring
│   │   └── settings/
│   │       └── page.tsx        # Export & clear portfolio
│   ├── components/
│   │   └── ThemeToggle.tsx     # Dark mode toggle button
│   ├── context/
│   │   ├── ThemeContext.tsx    # Theme state management
│   │   └── PortfolioContext.tsx # Portfolio state management
│   ├── lib/
│   │   └── csv-parsers/
│   │       ├── index.ts        # Parser exports + auto-detection
│   │       ├── wealthsimple.ts # WealthSimple CSV parser
│   │       └── generic.ts      # Generic CSV parser
│   └── public/
│       └── samples/
│           └── wealthsimple-sample.csv
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI application
│   │   ├── api/v1/
│   │   │   ├── health.py       # Health check endpoint
│   │   │   ├── mock.py         # Mock portfolio data
│   │   │   └── analysis.py     # Portfolio analysis endpoint
│   │   └── models/
│   └── venv/                   # Python virtual environment
├── docs/
│   ├── agent-workflow/
│   │   ├── REQ.md              # Requirements
│   │   ├── ARCH.md             # Architecture (v1.0)
│   │   ├── ARCH_V1.5.md        # Architecture (v1.5)
│   │   ├── TASKS.md            # Implementation tasks (v1.0)
│   │   ├── TASKS_V1.5.md       # Implementation tasks (v1.5)
│   │   ├── QA.md               # QA report (v1.0)
│   │   ├── QA_V1.5.md          # QA report (v1.5)
│   │   ├── CLAUDE.md           # Claude instructions
│   │   ├── GEMINI.md           # This file
│   │   └── ISSUES.md           # Known issues
│   ├── FINAL_REPORT.md         # Project closeout
│   └── RUN_STATE.md            # Pipeline state tracking
└── agents/
    ├── tony.md                 # Architect persona
    ├── peter.md                # Developer persona
    ├── heimdall.md             # QA persona
    └── pepper.md               # Analyst persona
```

---

## Common Tasks

### Add a New Page

1. Create directory: `frontend/app/<page-name>/page.tsx`
2. Add navigation link in layout.tsx
3. Style with Tailwind (include `dark:` classes)
4. Test in browser

### Add API Endpoint

1. Create route in `backend/app/api/v1/<endpoint>.py`
2. Define Pydantic models for request/response
3. Implement endpoint logic
4. Test with curl or Postman

### Update Theme Colors

1. Edit `frontend/tailwind.config.ts` (theme.extend.colors)
2. Update `frontend/app/globals.css` (CSS variables)
3. Test in both light and dark modes

### Add CSV Parser

1. Create `frontend/lib/csv-parsers/<format>.ts`
2. Implement parse function returning `Holding[]`
3. Update `index.ts` with detection logic
4. Test with sample CSV

---

## Code Patterns

### Component Template

```typescript
'use client';

import React from 'react';

interface Props {
  // Define props
}

export const ComponentName: React.FC<Props> = ({ prop1, prop2 }) => {
  return (
    <div className="bg-white dark:bg-dark-surface p-4 rounded-lg">
      {/* Component content */}
    </div>
  );
};
```

### Context Template

```typescript
'use client';

import React, { createContext, useContext, useState } from 'react';

interface ContextType {
  // Define context values
}

const Context = createContext<ContextType | undefined>(undefined);

export function Provider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState(initialValue);
  
  const value = {
    state,
    setState,
  };
  
  return (
    <Context.Provider value={value}>
      {children}
    </Context.Provider>
  );
}

export function useContextValue() {
  const context = useContext(Context);
  if (!context) {
    throw new Error('useContextValue must be used within Provider');
  }
  return context;
}
```

### API Endpoint Template

```python
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class RequestModel(BaseModel):
    field1: str
    field2: int

class ResponseModel(BaseModel):
    result: str

@router.post("/endpoint")
async def endpoint_handler(request: RequestModel) -> ResponseModel:
    # Implementation
    return ResponseModel(result="success")
```

---

## Testing Checklist

### Before Committing

- [ ] `npm run build` passes (frontend)
- [ ] Dev server runs without errors
- [ ] All pages load in browser
- [ ] Dark mode toggle works
- [ ] No console errors
- [ ] Import flow works (if changed)
- [ ] API endpoints respond (if changed)

### QA Verification

- [ ] Dashboard shows correct data
- [ ] Holdings table displays all stocks
- [ ] Analysis page shows risk score
- [ ] Import page auto-detects format
- [ ] Settings page export works
- [ ] Theme persists after reload
- [ ] Responsive on mobile/tablet

---

## Deployment

### Frontend (Vercel)

1. Connect GitHub repository
2. Build command: `npm run build`
3. Output directory: `.next`
4. Root directory: `frontend`
5. Environment variables: None required

### Backend (Railway)

1. Connect GitHub repository
2. Root directory: `backend`
3. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Environment variables: None required (v1.5)

---

## Troubleshooting

### Build Fails

```bash
cd frontend
npm run build
# Check error message
# Common issues: TypeScript errors, missing imports
```

### Theme Not Working

- Check `ThemeProvider` wraps app in `layout.tsx`
- Verify `darkMode: 'class'` in tailwind.config.ts
- Check localStorage: `localStorage.getItem('klyrsignals_theme')`

### Import Not Persisting

- Check `PortfolioContext.tsx` has `isInitialized` flag
- Verify `importHoldings()` is called
- Check localStorage: `localStorage.getItem('klyrsignals_portfolio')`

### API Not Responding

```bash
# Check backend is running
curl http://localhost:8000/api/health
# Expected: {"status": "healthy"}

# Check logs
cd backend
uvicorn app.main:app --reload
# Watch for errors
```

---

## Resources

- **Next.js Docs:** https://nextjs.org/docs
- **Tailwind CSS:** https://tailwindcss.com/docs
- **FastAPI:** https://fastapi.tiangolo.com
- **Recharts:** https://recharts.org

---

## When in Doubt

1. **Check CLAUDE.md** - Detailed architecture and patterns
2. **Check ARCH_V1.5.md** - v1.5 specific design
3. **Check TASKS_V1.5.md** - Implementation details
4. **Run dev server** - Test changes immediately
5. **Ask for clarification** - Don't guess
