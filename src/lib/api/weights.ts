import type { Weight, WeightCreate, WeightUpdate } from '$lib/types/weight';
import { invoke } from '@tauri-apps/api/core';

export const weightsApi = {
  /**
   * Get weight records for the last N days
   */
  async getWeights(days: number = 7): Promise<Weight[]> {
    return await invoke('get_weights', { days });
  },

  /**
   * Get weight by ID
   */
  async getWeightById(id: number): Promise<Weight> {
    return await invoke('get_weight_by_id', { id });
  },

  /**
   * Get weight by date
   */
  async getWeightByDate(date: string): Promise<Weight> {
    return await invoke('get_weight_by_date', { date });
  },

  /**
   * Create a new weight record
   */
  async createWeight(data: WeightCreate): Promise<Weight> {
    return await invoke('create_weight', { weightData: data });
  },

  /**
   * Update weight by ID
   */
  async updateWeightById(id: number, data: WeightUpdate): Promise<Weight> {
    return await invoke('update_weight', { id, weightData: data });
  },

  /**
   * Update weight by date
   */
  async updateWeightByDate(date: string, data: WeightUpdate): Promise<Weight> {
    return await invoke('update_weight_by_date', { date, weightData: data });
  },

  /**
   * Delete weight by ID
   */
  async deleteWeightById(id: number): Promise<void> {
    await invoke('delete_weight', { id });
  },

  /**
   * Delete weight by date
   */
  async deleteWeightByDate(date: string): Promise<void> {
    await invoke('delete_weight_by_date', { date });
  },
};
