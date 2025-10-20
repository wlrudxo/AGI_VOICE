export interface Weight {
  id: number;
  measuredDate: string;  // ISO date string (YYYY-MM-DD)
  weight: number;
  note: string | null;
  createdAt: string;     // ISO datetime string
}

export interface WeightCreate {
  measuredDate: string;
  weight: number;
  note?: string | null;
}

export interface WeightUpdate {
  measuredDate: string;
  weight: number;
  note?: string | null;
}
