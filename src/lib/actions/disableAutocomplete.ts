export function disableAutocomplete(node: HTMLElement) {
  const apply = (el: Element) => {
    if (el instanceof HTMLInputElement || el instanceof HTMLTextAreaElement) {
      if (el.getAttribute('data-allow-autocomplete') === 'true') {
        return;
      }

      el.setAttribute('autocomplete', 'off');
      el.setAttribute('autocorrect', 'off');
      el.setAttribute('autocapitalize', 'off');
      el.spellcheck = false;
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
    }
  };
}
