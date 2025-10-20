import { weightsApi } from '$lib/api/weights';
import type { Weight, WeightCreate, WeightUpdate } from '$lib/types/weight';

class WeightStore {
  weights = $state<Weight[]>([]);
  loading = $state(false);
  error = $state<string | null>(null);

  async fetchWeights(days: number = 7) {
    this.loading = true;
    this.error = null;
    try {
      this.weights = await weightsApi.getWeights(days);
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Failed to fetch weights';
    } finally {
      this.loading = false;
    }
  }

  async createWeight(data: WeightCreate) {
    this.loading = true;
    this.error = null;
    try {
      const newWeight = await weightsApi.createWeight(data);
      this.weights = [newWeight, ...this.weights].sort(
        (a, b) => new Date(b.measuredDate).getTime() - new Date(a.measuredDate).getTime()
      );
      return newWeight;
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Failed to create weight';
      throw err;
    } finally {
      this.loading = false;
    }
  }

  async updateWeightByDate(date: string, data: WeightUpdate) {
    this.loading = true;
    this.error = null;
    try {
      const updated = await weightsApi.updateWeightByDate(date, data);
      this.weights = this.weights.map((w) =>
        w.measuredDate === date ? updated : w
      );
      return updated;
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Failed to update weight';
      throw err;
    } finally {
      this.loading = false;
    }
  }

  async deleteWeightByDate(date: string) {
    this.loading = true;
    this.error = null;
    try {
      await weightsApi.deleteWeightByDate(date);
      this.weights = this.weights.filter((w) => w.measuredDate !== date);
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Failed to delete weight';
      throw err;
    } finally {
      this.loading = false;
    }
  }
}

export const weightStore = new WeightStore();
