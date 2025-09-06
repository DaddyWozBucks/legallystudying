// Simple in-memory store for document summaries
interface SummaryData {
  summary: string;
  key_points: string[];
  generated_at: string;
}

class SummaryStore {
  private summaries: Map<string, SummaryData> = new Map();

  getSummary(documentId: string): SummaryData | null {
    return this.summaries.get(documentId) || null;
  }

  setSummary(documentId: string, summary: SummaryData): void {
    this.summaries.set(documentId, summary);
  }

  clearSummary(documentId: string): void {
    this.summaries.delete(documentId);
  }

  clearAll(): void {
    this.summaries.clear();
  }
}

// Create a singleton instance
export const summaryStore = new SummaryStore();