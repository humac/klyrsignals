import { Holding } from '@/types/portfolio';

export interface WealthSimpleRow {
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
    throw new Error('CSV must have headers and at least one row');
  }

  const headers = lines[0].split(',').map(h => h.trim());
  const holdings: Holding[] = [];
  const holdingsMap = new Map<string, Holding>();

  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map(v => v.trim());
    const row: Record<string, string> = {};

    headers.forEach((header, index) => {
      row[header] = values[index];
    });

    const symbol = row.Symbol?.toUpperCase() || '';
    const quantity = parseFloat(row.Quantity || '0');
    const price = parseFloat(row.Price || '0');
    const commission = parseFloat(row.Commission || '0');
    const action = row.Action?.toUpperCase() as 'BUY' | 'SELL';
    const description = row.Description || row.symbol || '';

    if (!symbol || quantity === 0) {
      continue; // Skip invalid rows
    }

    if (action === 'BUY') {
      // Add or update holding with average cost
      const existing = holdingsMap.get(symbol);
      if (existing) {
        // Calculate new average cost
        const totalCost = (existing.quantity * existing.purchase_price) + (quantity * price) + commission;
        const totalQuantity = existing.quantity + quantity;
        existing.purchase_price = totalCost / totalQuantity;
        existing.quantity = totalQuantity;
      } else {
        // New holding
        holdingsMap.set(symbol, {
          symbol,
          quantity,
          purchase_price: (quantity * price + commission) / quantity, // Include commission in cost basis
          purchase_date: undefined,
          asset_class: 'stock' as const,
        });
      }
    } else if (action === 'SELL') {
      // Reduce or remove holding
      const existing = holdingsMap.get(symbol);
      if (existing) {
        existing.quantity = Math.max(0, existing.quantity - quantity);
        if (existing.quantity === 0) {
          holdingsMap.delete(symbol);
        }
      }
    }
  }

  return Array.from(holdingsMap.values());
}
