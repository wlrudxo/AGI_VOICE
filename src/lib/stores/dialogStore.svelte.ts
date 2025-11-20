// Global dialog store for easy access from any component
class DialogStore {
  private dialogComponent: any = null;

  setDialogComponent(component: any) {
    this.dialogComponent = component;
  }

  async confirm(message: string, title: string = '확인'): Promise<boolean> {
    if (!this.dialogComponent) {
      console.warn('Dialog component not initialized, falling back to native confirm');
      return confirm(message);
    }
    return this.dialogComponent.confirm(message, title);
  }

  async alert(message: string, title: string = '알림'): Promise<boolean> {
    if (!this.dialogComponent) {
      console.warn('Dialog component not initialized, falling back to native alert');
      alert(message);
      return true;
    }
    return this.dialogComponent.alert(message, title);
  }
}

export const dialogStore = new DialogStore();
