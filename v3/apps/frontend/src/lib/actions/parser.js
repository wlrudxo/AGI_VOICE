const KNOWN_ACTION_TYPES = new Set([
  'map',
  'update_map',
  'delete_map',
  'read_map',
  'read_dashboard',
]);

export function parseWithSegments(response) {
  const segments = [];
  const tagPattern = /<([^\n|>]+)(?:\|([^\n>]+))?>/g;
  let lastEnd = 0;
  let match;

  while ((match = tagPattern.exec(response)) !== null) {
    const actionType = match[1].trim();
    if (!KNOWN_ACTION_TYPES.has(actionType)) {
      continue;
    }

    if (match.index > lastEnd) {
      const textBefore = response.substring(lastEnd, match.index).trim();
      if (textBefore) {
        segments.push({ type: 'text', content: textBefore });
      }
    }

    segments.push({
      type: 'action',
      label: getActionLabel(actionType),
    });
    lastEnd = match.index + match[0].length;
  }

  if (lastEnd < response.length) {
    const textAfter = response.substring(lastEnd).trim();
    if (textAfter) {
      segments.push({ type: 'text', content: textAfter });
    }
  }

  if (segments.length === 0) {
    segments.push({ type: 'text', content: response });
  }

  return segments;
}

export function getActionLabel(actionType) {
  const labels = {
    map: '맵 추가',
    update_map: '맵 수정',
    delete_map: '맵 삭제',
    read_map: '맵 조회',
    read_dashboard: '대시보드 조회',
  };
  return labels[actionType] || actionType;
}
