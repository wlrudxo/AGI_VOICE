class DialogStore {
  async confirm(message, title = '확인') {
    console.warn(`DialogStore.confirm fallback: ${title}`);
    return window.confirm(message);
  }

  async alert(message, title = '알림') {
    console.warn(`DialogStore.alert fallback: ${title}`);
    window.alert(message);
    return true;
  }
}

export const dialogStore = new DialogStore();
