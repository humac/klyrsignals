export { parseGenericCSV } from './generic';
export { parseWealthSimpleCSV } from './wealthsimple';

export type CSVFormat = 'wealthsimple' | 'generic';

export function detectCSVFormat(headers: string[]): CSVFormat {
  const normalized = headers.map(h => h.toLowerCase().trim());
  
  // WealthSimple has these specific columns
  if (
    normalized.includes('trade date') &&
    normalized.includes('commission') &&
    (normalized.includes('action') || normalized.includes('buy/sell'))
  ) {
    return 'wealthsimple';
  }
  
  return 'generic';
}
