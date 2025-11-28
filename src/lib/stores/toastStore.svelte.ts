/**
 * Toast Store
 * 토스트 알림 상태 관리
 */

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: number;
  type: ToastType;
  message: string;
  duration: number;
}

class ToastStore {
  toasts = $state<Toast[]>([]);
  private nextId = 0;

  /**
   * 토스트 추가
   */
  add(message: string, type: ToastType = 'info', duration: number = 3000): number {
    const id = this.nextId++;

    this.toasts.push({
      id,
      type,
      message,
      duration
    });

    // 자동 제거
    if (duration > 0) {
      setTimeout(() => {
        this.remove(id);
      }, duration);
    }

    return id;
  }

  /**
   * 토스트 제거
   */
  remove(id: number): void {
    this.toasts = this.toasts.filter(t => t.id !== id);
  }

  /**
   * 성공 토스트
   */
  success(message: string, duration: number = 3000): number {
    return this.add(message, 'success', duration);
  }

  /**
   * 에러 토스트
   */
  error(message: string, duration: number = 4000): number {
    return this.add(message, 'error', duration);
  }

  /**
   * 경고 토스트
   */
  warning(message: string, duration: number = 3500): number {
    return this.add(message, 'warning', duration);
  }

  /**
   * 정보 토스트
   */
  info(message: string, duration: number = 3000): number {
    return this.add(message, 'info', duration);
  }

  /**
   * 모든 토스트 제거
   */
  clear(): void {
    this.toasts = [];
  }
}

export const toastStore = new ToastStore();
