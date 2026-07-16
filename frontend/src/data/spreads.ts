export interface SpreadType {
  id: string;
  count: number;
  tier: "free" | "pro";
  icon: string;
  schemeCount?: number;
}

// Display strings (name/desc/positions/schemes) live in the i18n locale
// files under tarot.spreads.<id> (all 6 languages), not here — this only
// carries the structural metadata the UI needs before it knows the
// user's language.
export const SPREADS: SpreadType[] = [
  { id: "card_of_day", count: 1, tier: "free", icon: "☀" },
  { id: "three_cards", count: 3, tier: "free", icon: "☰", schemeCount: 4 },
  { id: "celtic_cross", count: 10, tier: "pro", icon: "⊞" },
  { id: "horseshoe", count: 7, tier: "pro", icon: "⌓" },
  { id: "relationship", count: 7, tier: "pro", icon: "♡" },
  { id: "yes_no", count: 5, tier: "pro", icon: "?" },
  { id: "two_choices", count: 6, tier: "pro", icon: "⑂" },
  { id: "person", count: 5, tier: "pro", icon: "○" },
  { id: "year", count: 13, tier: "pro", icon: "▦" },
];
