# KlyrSignals v1.5 Architecture

**Version:** 1.5.0  
**Status:** 📐 Design Complete  
**Last Updated:** 2026-02-28  
**Author:** Tony (Architect)

---

## Overview

v1.5 adds **dark mode** and **WealthSimple import** to the v1.0 foundation. Both features are backward compatible and opt-in, requiring no breaking changes to existing functionality.

**Key Additions:**
- **Dark Mode:** Class-based theme toggle with localStorage persistence and system preference detection
- **WealthSimple Import:** Auto-detecting CSV parser for WealthSimple trade confirmations

---

## Dark Mode Architecture

### Theme System

| Component | Implementation | Details |
|-----------|---------------|---------|
| **Provider** | ThemeContext (React Context API) | Wraps entire app, provides theme state + toggle function |
| **Storage** | localStorage + system preference | User preference persisted; defaults to `prefers-color-scheme` |
| **Toggle Mechanism** | Class-based (`dark` class on `<html>`) | Tailwind `darkMode: 'class'` strategy |
| **Tailwind Config** | `darkMode: 'class'` | Enables `dark:` prefix for all utilities |

### Component Hierarchy

```
App
├── ThemeProvider
│   └── PortfolioProvider
│       └── RootLayout
│           ├── Header/Navigation
│           │   └── ThemeToggle (NEW)
│           └── Pages
│               ├── Dashboard (/)
│               ├── Import (/import)
│               ├── Holdings (/holdings)
│               ├── Analysis (/analysis)
│               └── Settings (/settings)
```

### Color Palette

| Element | Light Mode | Dark Mode | Tailwind Class |
|---------|-----------|-----------|----------------|
| **Background** | `#ffffff` | `#0f172a` | `bg-white` / `dark:bg-dark-bg` |
| **Surface** | `#f9fafb` | `#1e293b` | `bg-gray-50` / `dark:bg-dark-surface` |
| **Text Primary** | `#111827` | `#f9fafb` | `text-gray-900` / `dark:text-gray-100` |
| **Text Secondary** | `#6b7280` | `#9ca3af` | `text-gray-500` / `dark:text-gray-400` |
| **Border** | `#e5e7eb` | `#334155` | `border-gray-200` / `dark:border-dark-border` |
| **Primary (Blue)** | `#2563eb` | `#3b82f6` | `text-blue-600` / `dark:text-blue-500` |
| **Input Background** | `#ffffff` | `#1e293b` | `bg-white` / `dark:bg-dark-surface` |
| **Input Border** | `#d1d5db` | `#475569` | `border-gray-300` / `dark:border-gray-600` |

### Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class', // Enable class-based dark mode
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Custom dark mode palette
        dark: {
          bg: '#0f172a',      // slate-900
          surface: '#1e293b', // slate-800
          border: '#334155',  // slate-700
        }
      }
    }
  },
  plugins: []
}
```

### ThemeContext API

```typescript
// frontend/context/ThemeContext.tsx
interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  isDark: boolean;
}

// Usage in components:
const { theme, toggleTheme, isDark } = useTheme();
```

### Theme Detection Logic

```typescript
// 1. Check localStorage for user preference
// 2. If not found, check system preference (prefers-color-scheme)
// 3. Default to light mode if neither available

function getInitialTheme(): 'light' | 'dark' {
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem('klyrsignals-theme');
    if (stored === 'light' || stored === 'dark') {
      return stored;
    }
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
  }
  return 'light';
}
```

### Files Changed (Dark Mode)

| File | Action | Purpose |
|------|--------|---------|
| `tailwind.config.js` | Update | Add `darkMode: 'class'` and dark color palette |
| `globals.css` | Update | Add dark mode CSS variables |
| `context/ThemeContext.tsx` | CREATE | Theme provider and state management |
| `hooks/useTheme.ts` | CREATE | Custom hook for theme access |
| `components/ThemeToggle.tsx` | CREATE | Sun/Moon toggle button |
| `app/layout.tsx` | Update | Wrap with ThemeProvider, add ThemeToggle to nav |
| `app/page.tsx` | Update | Add `dark:` classes to all elements |
| `app/import/page.tsx` | Update | Add `dark:` classes to all elements |
| `app/holdings/page.tsx` | Update | Add `dark:` classes to all elements |
| `app/analysis/page.tsx` | Update | Add `dark:` classes to all elements |
| `app/settings/page.tsx` | Update | Add `dark:` classes to all elements |

---

## WealthSimple Import Architecture

### CSV Format Detection

**Auto-Detection Strategy:**
- Parse first row (headers) from uploaded CSV
- Check for WealthSimple-specific column names
- Route to appropriate parser based on detection

**WealthSimple Indicators:**
- Headers contain: `"Trade Date"` AND `"Commission"`
- Alternative: `"Symbol"` AND `"Net Amount"` AND `"Buy/Sell"`

**Fallback:**
- If WealthSimple format not detected, use generic parser (v1.0 logic)

### Parser Architecture

```
lib/csv-parsers/
├── index.ts              # Export all parsers, detection logic
├── wealthsimple.ts       # WealthSimple-specific parser (NEW)
└── generic.ts            # Existing v1.0 parser (extracted)
```

### Data Flow

```
1. User uploads CSV file
        ↓
2. Frontend reads file as text (FileReader API)
        ↓
3. Parse headers (first line)
        ↓
4. Detect format: detectCSVFormat(headers)
        ↓
5. Route to parser:
   - 'wealthsimple' → parseWealthSimpleCSV()
   - 'generic' → parseGenericCSV()
        ↓
6. Map to Holding[] interface
        ↓
7. Show preview table to user
        ↓
8. User confirms import
        ↓
9. Save to PortfolioContext (localStorage)
```

### WealthSimple CSV Format

**Typical Columns:**
| Column Name | Type | Mapping |
|-------------|------|---------|
| Trade Date | string | `purchase_date` |
| Symbol | string | `symbol` |
| Description | string | (ignored, or extract asset class) |
| Quantity | number | `quantity` |
| Price | number | `purchase_price` |
| Commission | number | (track for cost basis) |
| Net Amount | number | (validation: quantity × price + commission) |
| Buy/Sell | enum | `action` (BUY → add, SELL → reduce) |

### WealthSimple Parser Implementation

```typescript
// frontend/lib/csv-parsers/wealthsimple.ts
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

    const holding: Holding = {
      symbol: row.Symbol.toUpperCase(),
      quantity: Math.abs(parseFloat(row.Quantity)),
      purchase_price: parseFloat(row.Price),
      purchase_date: formatDate(row['Trade Date']),
      asset_class: inferAssetClass(row.Description),
    };

    // Handle SELL orders
    if (row['Buy/Sell'] === 'SELL') {
      // Mark for quantity reduction (handled in import logic)
      holding.quantity = -holding.quantity; // Negative for SELL
    }

    holdings.push(holding);
  }

  return holdings;
}

function detectCSVFormat(headers: string[]): 'wealthsimple' | 'generic' {
  const hasTradeDate = headers.some(h => h.toLowerCase().includes('trade date'));
  const hasCommission = headers.some(h => h.toLowerCase().includes('commission'));
  
  if (hasTradeDate && hasCommission) {
    return 'wealthsimple';
  }
  return 'generic';
}
```

### WealthSimple-Specific Handling

**BUY Orders:**
- Add new holding or update existing position
- Recalculate average cost basis if symbol already exists

**SELL Orders:**
- Reduce quantity of existing holding
- Remove holding if quantity reaches zero
- Track realized gains/losses (future feature)

**Commission Tracking:**
- Add commission to cost basis: `total_cost = (quantity × price) + commission`
- Store in metadata for tax reporting (future)

**Date Formatting:**
- WealthSimple uses: `YYYY-MM-DD` or `MM/DD/YYYY`
- Normalize to ISO format: `YYYY-MM-DD`

### Files Changed (WealthSimple Import)

| File | Action | Purpose |
|------|--------|---------|
| `lib/csv-parsers.ts` | CREATE | Export all parsers, detection logic |
| `lib/csv-parsers/wealthsimple.ts` | CREATE | WealthSimple-specific parser |
| `lib/csv-parsers/generic.ts` | CREATE | Extracted v1.0 generic parser |
| `app/import/page.tsx` | Update | Add auto-detection, route to parsers |

### Backend Enhancement (Optional - Phase 2)

**Server-Side Parser:**
```python
# backend/app/parsers/wealthsimple.py
def parse_wealthsimple_csv(csv_text: str) -> list[Holding]:
    """
    Parse WealthSimple trade confirmation CSV.
    Returns list of Holding models.
    """
    # Implementation mirrors frontend parser
    # Used for server-side import API endpoint
    pass
```

**New API Endpoint:**
```python
# POST /api/v1/import/wealthsimple
@app.post("/api/v1/import/wealthsimple", response_model=ImportResponse)
async def import_wealthsimple(file: UploadFile):
    """
    Upload and parse WealthSimple CSV export.
    Returns parsed holdings for preview before import.
    """
    csv_text = await file.read()
    holdings = parse_wealthsimple_csv(csv_text)
    return {"holdings": holdings, "format": "wealthsimple"}
```

**List Supported Formats:**
```python
# GET /api/v1/import/formats
@app.get("/api/v1/import/formats")
async def get_import_formats():
    return {
        "formats": [
            {"name": "generic", "description": "Generic CSV (symbol, quantity, price)"},
            {"name": "wealthsimple", "description": "WealthSimple trade confirmations"}
        ]
    }
```

---

## API Changes

### New Endpoints (Optional - Backend Parser)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/import/wealthsimple` | Server-side WealthSimple parsing | No |
| GET | `/api/v1/import/formats` | List supported import formats | No |

### Existing Endpoints

**No changes required** - All v1.0 endpoints remain backward compatible.

---

## Testing Strategy

### Dark Mode Testing

| Test Type | Method | Success Criteria |
|-----------|--------|------------------|
| **Manual Toggle** | Click theme toggle on each page | Theme switches immediately, all elements styled correctly |
| **Persistence** | Toggle theme, reload page | Theme persists after reload |
| **System Preference** | Change OS dark mode setting | App respects system preference on first load |
| **Visual Regression** | Screenshot all pages in both modes | 100% of UI elements styled in both modes |
| **Accessibility** | Test with screen reader | Theme toggle announced correctly |

**Test Checklist:**
- [ ] Dashboard page (light + dark)
- [ ] Import page (light + dark)
- [ ] Holdings page (light + dark)
- [ ] Analysis page (light + dark)
- [ ] Settings page (light + dark)
- [ ] Navigation header (light + dark)
- [ ] Footer (light + dark)
- [ ] All modal/dialog components (light + dark)
- [ ] All form inputs (light + dark)
- [ ] All charts (Recharts respects dark mode)

### WealthSimple Import Testing

| Test Type | Method | Success Criteria |
|-----------|--------|------------------|
| **Unit Tests** | Parser with sample WealthSimple CSV | 100% of rows parsed correctly |
| **Format Detection** | Upload WealthSimple + generic CSV | Correct parser auto-selected |
| **Integration** | Upload real WealthSimple export | Holdings appear in preview table |
| **Edge Cases** | SELL orders, partial sells, commissions | Handled correctly |
| **Error Handling** | Invalid format, missing columns | Clear error message shown |
| **Performance** | 1000-row CSV | Parse time <1 second |

**Sample WealthSimple CSV for Testing:**
```csv
Trade Date,Symbol,Description,Quantity,Price,Commission,Net Amount,Buy/Sell
2024-01-15,AAPL,APPLE INC,50,150.00,9.99,7509.99,BUY
2024-02-20,MSFT,MICROSOFT CORP,30,280.00,9.99,8409.99,BUY
2024-03-10,VTI,VANGUARD TOTAL STOCK MARKET ETF,100,220.00,0.00,22000.00,BUY
2024-04-05,AAPL,APPLE INC,20,175.00,9.99,3509.99,SELL
```

**Edge Cases to Test:**
- [ ] SELL order (quantity reduction)
- [ ] Partial sell (reduce but not eliminate position)
- [ ] Commission included in cost basis
- [ ] Multiple trades for same symbol (average cost)
- [ ] Missing optional columns (Description)
- [ ] Different date formats
- [ ] Negative quantities (should use absolute value)
- [ ] Invalid symbol (show warning, skip row)

---

## Migration Path

### Dark Mode Migration

- **No breaking changes**
- **Default behavior:** System preference (`prefers-color-scheme`)
- **User opt-in:** Toggle button to manually switch themes
- **Existing users:** No action required, app continues in light mode unless system is dark

### WealthSimple Import Migration

- **No breaking changes**
- **Existing generic CSV import:** Continues to work unchanged
- **Auto-detection:** Users don't need to select format manually
- **Fallback:** If WealthSimple detection fails, generic parser used

### Backward Compatibility Guarantee

✅ All v1.0 functionality remains intact  
✅ No API changes required for v1.5  
✅ localStorage schema unchanged  
✅ Existing portfolios unaffected  

---

## Success Metrics

### Dark Mode

| Metric | Target | Measurement |
|--------|--------|-------------|
| **UI Coverage** | 100% of elements styled | Visual audit of all pages |
| **Toggle Response** | <100ms | User perception (instant) |
| **Persistence** | 100% | Reload test |
| **System Preference** | 100% | Match OS setting on first load |

### WealthSimple Import

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Parse Success Rate** | 95% of real exports | User testing with actual WealthSimple CSVs |
| **Format Detection Accuracy** | 100% | Test with known formats |
| **Parse Performance** | <1s for 1000 rows | Performance testing |
| **Error Handling** | Clear messages for all failures | Manual testing |

---

## Performance Considerations

### Dark Mode

- **No runtime performance impact** - CSS-only theme switching
- **Bundle size:** +2-3KB (ThemeContext + toggle component)
- **First paint:** No delay (theme applied before render)

### WealthSimple Import

- **Parser performance:** O(n) where n = number of CSV rows
- **Memory:** Minimal (streaming parse, not loading entire file)
- **Target:** <1 second for 1000-row CSV

---

## Security Considerations

### Dark Mode

- No security implications (client-side CSS only)

### WealthSimple Import

- **Client-side parsing only** - CSV never sent to backend (unless optional server-side parser used)
- **No data persistence** - Holdings stored in localStorage (same as v1.0)
- **Input validation** - All parsed data validated against Holding schema
- **XSS prevention** - React auto-escapes all user-provided content

---

## Future Enhancements (v1.6+)

### Dark Mode
- Custom color themes (blue, purple, green accents)
- Auto-switch based on time of day
- Per-page theme overrides

### WealthSimple Import
- Support for WealthSimple RRSP/TFSA account types
- Import trade history (not just current holdings)
- Automatic commission tracking for tax reporting
- Support for other broker formats (Questrade, Interactive Brokers)
- Direct API integration with WealthSimple (OAuth)

---

## Appendix: Implementation Checklist

### Dark Mode

- [ ] Update `tailwind.config.js` with `darkMode: 'class'`
- [ ] Add dark color palette to Tailwind config
- [ ] Create `ThemeContext.tsx` with provider
- [ ] Create `useTheme` hook
- [ ] Create `ThemeToggle` component (Sun/Moon icons)
- [ ] Update `globals.css` with dark mode CSS variables
- [ ] Update `layout.tsx` with ThemeProvider wrapper
- [ ] Add ThemeToggle to navigation header
- [ ] Update all 5 pages with `dark:` classes
- [ ] Test on all pages (light + dark modes)
- [ ] Verify localStorage persistence
- [ ] Verify system preference detection

### WealthSimple Import

- [ ] Extract generic parser to `lib/csv-parsers/generic.ts`
- [ ] Create `lib/csv-parsers/wealthsimple.ts`
- [ ] Create `lib/csv-parsers/index.ts` with detection logic
- [ ] Update `import/page.tsx` with auto-detection
- [ ] Add WealthSimple sample CSV for testing
- [ ] Test with real WealthSimple exports
- [ ] Handle SELL orders correctly
- [ ] Handle commission in cost basis
- [ ] Add error handling for invalid formats
- [ ] Write unit tests for parsers
- [ ] (Optional) Add backend parser endpoint

---

**Architecture Sign-off:** ✅ Complete  
**Next Phase:** Peter (Developer) implementation  
**Handoff:** TASKS_V1.5.md generated with bounded tasks
