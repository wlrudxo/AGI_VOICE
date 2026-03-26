export function disableAutocomplete(node: HTMLElement) {
  const apply = (element: Element) => {
    if (element instanceof HTMLInputElement || element instanceof HTMLTextAreaElement) {
      if (element.getAttribute('data-allow-autocomplete') === 'true') {
        return;
      }

      element.setAttribute('autocomplete', 'off');
      element.setAttribute('autocorrect', 'off');
      element.setAttribute('autocapitalize', 'off');
      element.spellcheck = false;
    }
  };

  node.querySelectorAll('input, textarea').forEach(apply);

  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      mutation.addedNodes.forEach((added) => {
        if (!(added instanceof HTMLElement)) {
          return;
        }

        if (added.matches('input, textarea')) {
          apply(added);
        }

        added.querySelectorAll?.('input, textarea').forEach(apply);
      });
    }
  });

  observer.observe(node, { childList: true, subtree: true });

  return {
    destroy() {
      observer.disconnect();
    },
  };
}
