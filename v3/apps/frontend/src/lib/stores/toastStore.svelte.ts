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

  add(message: string, type: ToastType = 'info', duration: number = 3000): number {
    const id = this.nextId++;

    this.toasts.push({
      id,
      type,
      message,
      duration,
    });

    if (duration > 0) {
      setTimeout(() => {
        this.remove(id);
      }, duration);
    }

    return id;
  }

  remove(id: number): void {
    this.toasts = this.toasts.filter((toast) => toast.id !== id);
  }

  success(message: string, duration: number = 3000): number {
    return this.add(message, 'success', duration);
  }

  error(message: string, duration: number = 4000): number {
    return this.add(message, 'error', duration);
  }

  warning(message: string, duration: number = 3500): number {
    return this.add(message, 'warning', duration);
  }

  info(message: string, duration: number = 3000): number {
    return this.add(message, 'info', duration);
  }

  clear(): void {
    this.toasts = [];
  }
}

export const toastStore = new ToastStore();
