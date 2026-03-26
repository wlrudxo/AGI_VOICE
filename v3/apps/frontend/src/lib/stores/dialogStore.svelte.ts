class DialogStore {
  private dialogComponent: {
    confirm: (message: string, title?: string) => Promise<boolean>;
    alert: (message: string, title?: string) => Promise<boolean>;
  } | null = null;

  setDialogComponent(component: {
    confirm: (message: string, title?: string) => Promise<boolean>;
    alert: (message: string, title?: string) => Promise<boolean>;
  }): void {
    this.dialogComponent = component;
  }

  async confirm(message: string, title = '확인'): Promise<boolean> {
    if (!this.dialogComponent) {
      console.warn('Dialog component not initialized, falling back to native confirm');
      return window.confirm(message);
    }
    return this.dialogComponent.confirm(message, title);
  }

  async alert(message: string, title = '알림'): Promise<boolean> {
    if (!this.dialogComponent) {
      console.warn('Dialog component not initialized, falling back to native alert');
      window.alert(message);
      return true;
    }
    return this.dialogComponent.alert(message, title);
  }
}

export const dialogStore = new DialogStore();
