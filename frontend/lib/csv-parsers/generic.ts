import { Holding } from '@/types/portfolio';

export interface GenericCSVRow {
  symbol: string;
  quantity: number;
  purchase_price: number;
  [key: string]: string | number;
}

export function parseGenericCSV(csvText: string): Holding[] {
  const lines = csvText.trim().split('\n');
  if (lines.length < 2) {
    throw new Error('CSV must have headers and at least one row');
  }

  const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
  const holdings: Holding[] = [];

  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map(v => v.trim());
    const row: Record<string, string | number> = {};

    headers.forEach((header, index) => {
      row[header] = values[index];
    });

    // Map to Holding interface
    const holding: Holding = {
      symbol: String(row.symbol || row.ticker || '').toUpperCase(),
      quantity: Number(row.quantity || row.shares || 0),
      purchase_price: Number(row.purchase_price || row.cost || row.price || 0),
      purchase_date: String(row.purchase_date || row.date || '') || undefined,
      asset_class: (row.asset_class as any) || 'stock',
    };

    if (holding.symbol && holding.quantity > 0) {
      holdings.push(holding);
    }
  }

  return holdings;
}
