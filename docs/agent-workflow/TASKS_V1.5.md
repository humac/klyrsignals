# KlyrSignals v1.5 Implementation Tasks

**Version:** 1.5.0  
**Status:** 📋 Ready for Implementation  
**Last Updated:** 2026-02-28  
**Author:** Tony (Architect)

---

## Summary

**Total Estimated Time:** ~10 hours  
**Priority:** Dark Mode first (foundational), then WealthSimple Import  
**Dependencies:** None (both features independent)

---

## Phase 1: Dark Mode Implementation (~5 hours)

### Task 1.1: Update Tailwind Configuration
**Priority:** 🔴 HIGH (foundational)  
**Estimated Time:** 30 min  
**Files:** `frontend/tailwind.config.js`

**Acceptance Criteria:**
- [ ] Add `darkMode: 'class'` to config
- [ ] Define dark color palette in `theme.extend.colors.dark`
- [ ] Config validates without errors

**Implementation:**
```javascript
module.exports = {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#0f172a',
          surface: '#1e293b',
          border: '#334155',
        }
      }
    }
  },
  plugins: []
}
```

---

### Task 1.2: Create ThemeContext
**Priority:** 🔴 HIGH  
**Estimated Time:** 45 min  
**Files:** `frontend/context/ThemeContext.tsx` (NEW)

**Acceptance Criteria:**
- [ ] Context provides `theme`, `toggleTheme`, `isDark`
- [ ] Reads from localStorage on mount
- [ ] Falls back to system preference
- [ ] Persists changes to localStorage
- [ ] Updates `document.documentElement.classList`

**Implementation Notes:**
- Wrap app in `ThemeProvider`
- Use `useState` for theme state
- Use `useEffect` for localStorage + system preference detection
- Provide toggle function that switches theme

---

### Task 1.3: Create useTheme Hook
**Priority:** 🔴 HIGH  
**Estimated Time:** 15 min  
**Files:** `frontend/hooks/useTheme.ts` (NEW)

**Acceptance Criteria:**
- [ ] Exports `useTheme` custom hook
- [ ] Returns context values: `theme`, `toggleTheme`, `isDark`
- [ ] Throws error if used outside ThemeProvider

**Implementation:**
```typescript
import { useContext } from 'react';
import { ThemeContext } from '../context/ThemeContext';

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}
```

---

### Task 1.4: Create ThemeToggle Component
**Priority:** 🟡 MEDIUM  
**Estimated Time:** 30 min  
**Files:** `frontend/components/ThemeToggle.tsx` (NEW)

**Acceptance Criteria:**
- [ ] Renders Sun icon (light mode) / Moon icon (dark mode)
- [ ] Click toggles theme
- [ ] Accessible (aria-label, keyboard navigation)
- [ ] Styled to match navigation

**Implementation Notes:**
- Use SVG icons for Sun/Moon
- Use `useTheme` hook for state and toggle
- Add hover states and transitions
- Consider: Lucide React icons or custom SVG

---

### Task 1.5: Update globals.css with Dark Colors
**Priority:** 🔴 HIGH  
**Estimated Time:** 30 min  
**Files:** `frontend/app/globals.css`

**Acceptance Criteria:**
- [ ] Add CSS variables for dark mode colors
- [ ] Use `@media (prefers-color-scheme: dark)` for system preference
- [ ] Define all colors from palette

**Implementation:**
```css
@import "tailwindcss";

:root {
  --background: #ffffff;
  --foreground: #171717;
  --surface: #f9fafb;
  --border: #e5e7eb;
  --text-secondary: #6b7280;
}

@media (prefers-color-scheme: dark) {
  :root {
    --background: #0f172a;
    --foreground: #f9fafb;
    --surface: #1e293b;
    --border: #334155;
    --text-secondary: #9ca3af;
  }
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-surface: var(--surface);
  --color-border: var(--border);
  --color-text-secondary: var(--text-secondary);
  --font-sans: var(--font-geist-sans);
  --font-mono: var(--font-geist-mono);
}

body {
  background: var(--background);
  color: var(--foreground);
  font-family: Arial, Helvetica, sans-serif;
}
```

---

### Task 1.6: Update Dashboard Page with Dark Classes
**Priority:** 🟡 MEDIUM  
**Estimated Time:** 30 min  
**Files:** `frontend/app/page.tsx`

**Acceptance Criteria:**
- [ ] All backgrounds use `dark:bg-dark-bg` or `dark:bg-dark-surface`
- [ ] All text uses `dark:text-gray-100` / `dark:text-gray-400`
- [ ] All borders use `dark:border-dark-border`
- [ ] Cards/surfaces styled for dark mode
- [ ] Charts (Recharts) visible in dark mode

**Implementation Pattern:**
```tsx
// Before:
<div className="bg-white border border-gray-200">
  <h1 className="text-gray-900">Dashboard</h1>
</div>

// After:
<div className="bg-white dark:bg-dark-surface border border-gray-200 dark:border-dark-border">
  <h1 className="text-gray-900 dark:text-gray-100">Dashboard</h1>
</div>
```

---

### Task 1.7: Update Import Page with Dark Classes
**Priority:** 🟡 MEDIUM  
**Estimated Time:** 30 min  
**Files:** `frontend/app/import/page.tsx`

**Acceptance Criteria:**
- [ ] All backgrounds use dark mode variants
- [ ] All text uses dark mode variants
- [ ] All borders use dark mode variants
- [ ] Form inputs styled for dark mode
- [ ] Tables styled for dark mode
- [ ] Success/error states visible in dark mode

**Special Attention:**
- Textarea background/border
- Input field backgrounds
- Table headers (bg-gray-50 → dark:bg-dark-surface)
- Success message (bg-green-50 → needs dark variant)

---

### Task 1.8: Update Holdings Page with Dark Classes
**Priority:** 🟡 MEDIUM  
**Estimated Time:** 30 min  
**Files:** `frontend/app/holdings/page.tsx`

**Acceptance Criteria:**
- [ ] All elements styled for dark mode
- [ ] Tables readable in dark mode
- [ ] Action buttons visible
- [ ] Modal/dialogs (if any) styled

---

### Task 1.9: Update Analysis Page with Dark Classes
**Priority:** 🟡 MEDIUM  
**Estimated Time:** 30 min  
**Files:** `frontend/app/analysis/page.tsx`

**Acceptance Criteria:**
- [ ] All elements styled for dark mode
- [ ] Charts (Recharts) visible with dark background
- [ ] Warning banners readable
- [ ] Risk gauge visible

**Special Attention:**
- Recharts may need custom styling for dark mode
- Check chart tooltips, legends, axes

---

### Task 1.10: Update Settings Page with Dark Classes
**Priority:** 🟡 MEDIUM  
**Estimated Time:** 30 min  
**Files:** `frontend/app/settings/page.tsx`

**Acceptance Criteria:**
- [ ] All elements styled for dark mode
- [ ] Form controls styled
- [ ] Select dropdowns readable

---

### Task 1.11: Add ThemeToggle to Header
**Priority:** 🟡 MEDIUM  
**Estimated Time:** 20 min  
**Files:** `frontend/app/layout.tsx`

**Acceptance Criteria:**
- [ ] ThemeToggle component added to navigation
- [ ] Positioned in header (right side or near logo)
- [ ] Accessible from all pages
- [ ] ThemeProvider wraps entire app

**Implementation:**
```tsx
import { ThemeProvider } from '@/context/ThemeContext';
import { ThemeToggle } from '@/components/ThemeToggle';

// In RootLayout:
<ThemeProvider>
  <nav className="...">
    <div className="flex items-center">
      <a href="/" className="...">KlyrSignals</a>
      {/* Navigation links */}
    </div>
    <div className="flex items-center">
      <ThemeToggle />
    </div>
  </nav>
  {children}
</ThemeProvider>
```

---

### Task 1.12: Test and Verify All Pages
**Priority:** 🔴 HIGH (QA)  
**Estimated Time:** 30 min  
**Files:** All pages

**Acceptance Criteria:**
- [ ] Toggle theme on Dashboard - all elements styled correctly
- [ ] Toggle theme on Import - all elements styled correctly
- [ ] Toggle theme on Holdings - all elements styled correctly
- [ ] Toggle theme on Analysis - all elements styled correctly
- [ ] Toggle theme on Settings - all elements styled correctly
- [ ] Reload page - theme persists
- [ ] Test with system dark mode - respects preference on first load
- [ ] Check navigation header in both modes
- [ ] Check footer in both modes
- [ ] Verify charts visible in dark mode

**Testing Protocol:**
1. Open each page in browser
2. Toggle theme (light → dark → light)
3. Screenshot both modes
4. Reload page, verify theme persists
5. Check browser console for errors

---

## Phase 2: WealthSimple Import Implementation (~5 hours)

### Task 2.1: Extract Generic CSV Parser
**Priority:** 🔴 HIGH (foundational)  
**Estimated Time:** 30 min  
**Files:** `frontend/lib/csv-parsers/generic.ts` (NEW)

**Acceptance Criteria:**
- [ ] Extract current parsing logic from `import/page.tsx`
- [ ] Export `parseGenericCSV` function
- [ ] Maintain same behavior as v1.0
- [ ] Add TypeScript types

**Implementation:**
```typescript
// frontend/lib/csv-parsers/generic.ts
import { Holding } from '@/types/portfolio';

export function parseGenericCSV(csvText: string): Holding[] {
  const lines = csvText.trim().split('\n');
  if (lines.length < 2) {
    throw new Error('CSV must have header row and at least one data row');
  }

  const headers = lines[0].toLowerCase().split(',').map(h => h.trim());
  const holdings: Holding[] = [];

  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map(v => v.trim());
    if (values.length < 2) continue;

    const row: Record<string, string> = {};
    headers.forEach((header, idx) => {
      if (idx < values.length) {
        row[header] = values[idx];
      }
    });

    const symbol = row.symbol || row.ticker || row[0];
    const quantity = parseFloat(row.quantity || row.shares || row[1] || '0');
    const purchasePrice = parseFloat(row.purchase_price || row.price || row.cost || row[2] || '0');

    if (symbol && quantity > 0 && purchasePrice > 0) {
      holdings.push({
        symbol: symbol.toUpperCase(),
        quantity,
        purchase_price: purchasePrice,
        purchase_date: row.purchase_date || row.date || undefined,
        asset_class: (row.asset_class as any) || 'stock',
      });
    }
  }

  if (holdings.length === 0) {
    throw new Error('No valid holdings found in CSV');
  }

  return holdings;
}
```

---

### Task 2.2: Research WealthSimple CSV Format
**Priority:** 🟡 MEDIUM  
**Estimated Time:** 20 min  
**Files:** Research only

**Acceptance Criteria:**
- [ ] Confirm WealthSimple CSV column names
- [ ] Identify required vs optional columns
- [ ] Note date format used
- [ ] Note how BUY/SELL indicated

**Research Sources:**
- WealthSimple help docs
- Sample CSV exports from users
- Community forums

**Expected Format:**
```
Trade Date,Symbol,Description,Quantity,Price,Commission,Net Amount,Buy/Sell
```

---

### Task 2.3: Create WealthSimple Parser
**Priority:** 🔴 HIGH  
**Estimated Time:** 45 min  
**Files:** `frontend/lib/csv-parsers/wealthsimple.ts` (NEW)

**Acceptance Criteria:**
- [ ] Export `parseWealthSimpleCSV` function
- [ ] Handle all WealthSimple columns
- [ ] Map to Holding interface
- [ ] Handle BUY orders (positive quantity)
- [ ] Handle SELL orders (negative quantity or separate handling)
- [ ] Include commission in cost basis calculation
- [ ] Format dates correctly

**Implementation:**
```typescript
// frontend/lib/csv-parsers/wealthsimple.ts
import { Holding } from '@/types/portfolio';

interface WealthSimpleRow {
  tradeDate: string;
  symbol: string;
  description: string;
  quantity: number;
  price: number;
  commission: number;
  netAmount: number;
  action: 'BUY' | 'SELL';
}

export function parseWealthSimpleCSV(csvText: string): Holding[] {
  const lines = csvText.trim().split('\n');
  if (lines.length < 2) {
    throw new Error('CSV must have header row and at least one data row');
  }

  const headers = parseCSVLine(lines[0]);
  const holdings: Holding[] = [];

  for (let i = 1; i < lines.length; i++) {
    const values = parseCSVLine(lines[i]);
    const row = mapRowToObject(headers, values);

    const isSell = row['Buy/Sell']?.toUpperCase() === 'SELL';
    const quantity = Math.abs(parseFloat(row.Quantity || '0'));
    const price = parseFloat(row.Price || '0');
    const commission = parseFloat(row.Commission || '0');
    
    // Calculate adjusted cost basis (include commission)
    const adjustedPrice = isSell ? price : (quantity * price + commission) / quantity;

    const holding: Holding = {
      symbol: row.Symbol?.toUpperCase() || '',
      quantity: isSell ? -quantity : quantity,
      purchase_price: adjustedPrice,
      purchase_date: formatDate(row['Trade Date']),
      asset_class: inferAssetClass(row.Description),
    };

    holdings.push(holding);
  }

  return holdings;
}

// Helper functions
function parseCSVLine(line: string): string[] {
  // Handle CSV with potential quoted fields
  return line.split(',').map(field => field.trim());
}

function mapRowToObject(headers: string[], values: string[]): Record<string, string> {
  const obj: Record<string, string> = {};
  headers.forEach((header, idx) => {
    obj[header] = values[idx] || '';
  });
  return obj;
}

function formatDate(dateStr: string): string | undefined {
  if (!dateStr) return undefined;
  // Try to parse various formats
  // Return ISO format: YYYY-MM-DD
  return dateStr;
}

function inferAssetClass(description: string): string {
  if (!description) return 'stock';
  const lower = description.toLowerCase();
  if (lower.includes('etf')) return 'etf';
  if (lower.includes('fund')) return 'mutual_fund';
  if (lower.includes('crypto') || lower.includes('bitcoin')) return 'crypto';
  return 'stock';
}
```

---

### Task 2.4: Add Auto-Detection Logic
**Priority:** 🔴 HIGH  
**Estimated Time:** 30 min  
**Files:** `frontend/lib/csv-parsers/index.ts` (NEW)

**Acceptance Criteria:**
- [ ] Export all parsers from single entry point
- [ ] Export `detectCSVFormat` function
- [ ] Export `parseCSV` function (auto-detects and routes)
- [ ] Detection based on column headers

**Implementation:**
```typescript
// frontend/lib/csv-parsers/index.ts
export { parseGenericCSV } from './generic';
export { parseWealthSimpleCSV } from './wealthsimple';

export type CSVFormat = 'wealthsimple' | 'generic';

export function detectCSVFormat(csvText: string): CSVFormat {
  const lines = csvText.trim().split('\n');
  if (lines.length < 1) {
    return 'generic';
  }

  const headers = lines[0].toLowerCase().split(',').map(h => h.trim());
  
  // WealthSimple indicators
  const hasTradeDate = headers.some(h => h.includes('trade date'));
  const hasCommission = headers.some(h => h.includes('commission'));
  const hasBuySell = headers.some(h => h.includes('buy') && h.includes('sell'));
  
  if (hasTradeDate && hasCommission) {
    return 'wealthsimple';
  }
  
  return 'generic';
}

export function parseCSV(csvText: string): { holdings: Holding[]; format: CSVFormat } {
  const format = detectCSVFormat(csvText);
  
  let holdings;
  if (format === 'wealthsimple') {
    holdings = parseWealthSimpleCSV(csvText);
  } else {
    holdings = parseGenericCSV(csvText);
  }
  
  return { holdings, format };
}
```

---

### Task 2.5: Update Import Page with Format Detection
**Priority:** 🔴 HIGH  
**Estimated Time:** 30 min  
**Files:** `frontend/app/import/page.tsx`

**Acceptance Criteria:**
- [ ] Import new `parseCSV` function from `lib/csv-parsers`
- [ ] Replace inline `parseCSV` function with imported one
- [ ] Show detected format in UI (optional: "Detected: WealthSimple format")
- [ ] Maintain same preview/confirm flow

**Implementation:**
```typescript
import { parseCSV, CSVFormat } from '@/lib/csv-parsers';

// In handlePreview:
const handlePreview = () => {
  try {
    const { holdings, format } = parseCSV(csvText);
    setParsedHoldings(holdings);
    setDetectedFormat(format); // Optional: show in UI
    setStep('preview');
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Failed to parse CSV');
  }
};
```

---

### Task 2.6: Add WealthSimple Sample CSV for Testing
**Priority:** 🟢 LOW  
**Estimated Time:** 15 min  
**Files:** `frontend/public/samples/wealthsimple-sample.csv` (NEW)

**Acceptance Criteria:**
- [ ] Create sample CSV with realistic data
- [ ] Include BUY and SELL orders
- [ ] Include multiple symbols
- [ ] Include commission amounts

**Sample Content:**
```csv
Trade Date,Symbol,Description,Quantity,Price,Commission,Net Amount,Buy/Sell
2024-01-15,AAPL,APPLE INC,50,150.00,9.99,7509.99,BUY
2024-02-20,MSFT,MICROSOFT CORP,30,280.00,9.99,8409.99,BUY
2024-03-10,VTI,VANGUARD TOTAL STOCK MARKET ETF,100,220.00,0.00,22000.00,BUY
2024-04-05,AAPL,APPLE INC,20,175.00,9.99,3509.99,SELL
```

---

### Task 2.7: Test with Real WealthSimple Exports
**Priority:** 🔴 HIGH (QA)  
**Estimated Time:** 45 min  
**Files:** Testing only

**Acceptance Criteria:**
- [ ] Upload sample WealthSimple CSV
- [ ] Verify all rows parsed correctly
- [ ] Verify BUY orders add holdings
- [ ] Verify SELL orders reduce holdings
- [ ] Verify commission included in cost basis
- [ ] Verify dates formatted correctly
- [ ] Test with at least 2-3 different real exports

**Testing Protocol:**
1. Upload sample CSV
2. Check preview table matches expected values
3. Import holdings
4. Verify holdings appear correctly in portfolio
5. Test edge cases (SELL, partial sell, etc.)

---

### Task 2.8: Handle Edge Cases
**Priority:** 🟡 MEDIUM  
**Estimated Time:** 30 min  
**Files:** `frontend/lib/csv-parsers/wealthsimple.ts`, `frontend/app/import/page.tsx`

**Acceptance Criteria:**
- [ ] Handle missing optional columns (Description)
- [ ] Handle invalid dates (show error, skip row)
- [ ] Handle invalid symbols (show error, skip row)
- [ ] Handle zero quantity (skip row)
- [ ] Handle negative prices (show error)
- [ ] Show clear error messages for invalid CSV
- [ ] Handle very large files (1000+ rows)

**Error Messages:**
- "Invalid date format in row X"
- "Invalid symbol in row X"
- "Missing required column: [column name]"
- "No valid holdings found in CSV"

---

### Task 2.9: Write Unit Tests for Parsers
**Priority:** 🟡 MEDIUM  
**Estimated Time:** 45 min  
**Files:** `frontend/lib/csv-parsers/__tests__/parsers.test.ts` (NEW)

**Acceptance Criteria:**
- [ ] Test generic parser with valid CSV
- [ ] Test generic parser with invalid CSV
- [ ] Test WealthSimple parser with valid CSV
- [ ] Test WealthSimple parser with BUY orders
- [ ] Test WealthSimple parser with SELL orders
- [ ] Test format detection logic
- [ ] Test edge cases (empty CSV, missing columns)

**Test Framework:** Jest (existing in project)

**Example Test:**
```typescript
describe('parseWealthSimpleCSV', () => {
  it('should parse BUY orders correctly', () => {
    const csv = `Trade Date,Symbol,Description,Quantity,Price,Commission,Net Amount,Buy/Sell
2024-01-15,AAPL,APPLE INC,50,150.00,9.99,7509.99,BUY`;
    
    const holdings = parseWealthSimpleCSV(csv);
    expect(holdings).toHaveLength(1);
    expect(holdings[0].symbol).toBe('AAPL');
    expect(holdings[0].quantity).toBe(50);
    expect(holdings[0].purchase_price).toBeCloseTo(150.20); // Includes commission
  });

  it('should handle SELL orders as negative quantity', () => {
    const csv = `Trade Date,Symbol,Description,Quantity,Price,Commission,Net Amount,Buy/Sell
2024-04-05,AAPL,APPLE INC,20,175.00,9.99,3509.99,SELL`;
    
    const holdings = parseWealthSimpleCSV(csv);
    expect(holdings[0].quantity).toBe(-20);
  });
});
```

---

## Task Dependencies

```
Dark Mode:
1.1 (Tailwind) → 1.2 (ThemeContext) → 1.3 (useTheme) → 1.4 (ThemeToggle)
                                    ↓
1.5 (globals.css) → 1.6-1.10 (Pages) → 1.11 (Add to header) → 1.12 (Test)

WealthSimple:
2.1 (Extract generic) → 2.3 (WealthSimple parser) → 2.4 (Auto-detect) → 2.5 (Update import page)
                        ↓
                    2.2 (Research) - parallel

2.6 (Sample CSV) → 2.7 (Test) → 2.8 (Edge cases) → 2.9 (Unit tests)
```

---

## Recommended Implementation Order

**Day 1: Dark Mode Foundation (3 hours)**
1. Task 1.1: Tailwind config (30 min)
2. Task 1.2: ThemeContext (45 min)
3. Task 1.3: useTheme hook (15 min)
4. Task 1.4: ThemeToggle (30 min)
5. Task 1.5: globals.css (30 min)
6. Task 1.11: Add to header (20 min)
7. Test foundation (30 min)

**Day 2: Dark Mode Pages (2 hours)**
1. Task 1.6: Dashboard (30 min)
2. Task 1.7: Import (30 min)
3. Task 1.8: Holdings (30 min)
4. Task 1.9: Analysis (30 min)
5. Task 1.10: Settings (30 min)
6. Task 1.12: Full test (30 min)

**Day 3: WealthSimple Import (3 hours)**
1. Task 2.1: Extract generic parser (30 min)
2. Task 2.2: Research format (20 min)
3. Task 2.3: Create WealthSimple parser (45 min)
4. Task 2.4: Auto-detection (30 min)
5. Task 2.5: Update import page (30 min)
6. Task 2.6: Sample CSV (15 min)
7. Task 2.7: Testing (45 min)
8. Task 2.8: Edge cases (30 min)
9. Task 2.9: Unit tests (45 min)

**Buffer/Contingency:** 2 hours

**Total:** ~10 hours

---

## Definition of Done (per task)

Each task is complete when:
- [ ] Code implemented per acceptance criteria
- [ ] No TypeScript errors
- [ ] No console errors in browser
- [ ] Manual testing passed
- [ ] Code follows existing project patterns
- [ ] (For parser tasks) Unit tests written and passing

---

## Handoff Checklist (for Peter)

Before marking v1.5 complete:
- [ ] All 12 Dark Mode tasks complete
- [ ] All 9 WealthSimple tasks complete
- [ ] Dev server runs without errors
- [ ] All 5 pages load in browser (light mode)
- [ ] All 5 pages load in browser (dark mode)
- [ ] Theme toggle works on all pages
- [ ] Theme persists after reload
- [ ] WealthSimple CSV import works
- [ ] Generic CSV import still works
- [ ] Unit tests passing (`npm test`)
- [ ] Build passes (`npm run build`)
- [ ] Screenshots captured as proof
- [ ] Ready for Heimdall QA

---

**Tasks Sign-off:** ✅ Complete  
**Ready for:** Peter (Developer) implementation  
**Estimated Duration:** ~10 hours
