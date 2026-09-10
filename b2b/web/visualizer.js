// Decorative, audio-driven art. It never controls playback or reads track data.
export function createVisualizer(canvas) {
  const context = canvas.getContext('2d', { alpha: false });
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const palettes = [
    ['#ff7ea8', '#fbbe91', '#98adff'],
    ['#b6d784', '#ffe0a8', '#bd9edc'],
    ['#9fb8fb', '#f8a5ba', '#c9f0c0'],
    ['#ffb890', '#d2b6f3', '#e0ed8f'],
    ['#dd91ad', '#91b9b7', '#f5d09a'],
    ['#b3a2f2', '#dfe798', '#e9a8a0'],
  ];
  let identityKey, seed = 0, palette = palettes[0], bins;
  let lastDraw = -Infinity, phase = 0, width = 0, height = 0, scale = 0;
  let rendered = false, energy = [0, 0, 0];
  const hash = text => {
    let value = 2166136261;
    for (const char of text) value = Math.imul(value ^ char.charCodeAt(0), 16777619);
    return value >>> 0;
  };
  function spectrum(analyser) {
    if (!analyser) return [0, 0, 0];
    if (!bins || bins.length !== analyser.frequencyBinCount) bins = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(bins);
    const step = (analyser.context?.sampleRate || 44100) / (2 * bins.length);
    return [[35, 220], [220, 2200], [2200, 10000]].map(([low, high]) => {
      const first = Math.min(bins.length - 1, Math.max(1, Math.floor(low / step)));
      const end = Math.min(bins.length, Math.max(first + 1, Math.ceil(high / step)));
      let sum = 0;
      for (let i = first; i < end; i++) sum += bins[i] * bins[i];
      return Math.sqrt(sum / Math.max(1, end - first)) / 255;
    });
  }
  function ribbon(index) {
    // Keep reflected-light facets below two CSS pixels on ordinary screens.
    // The cap bounds work on very wide displays; animation already runs at 30fps.
    const points = [], count = Math.min(1000, Math.max(120, Math.ceil(width * 1.16 / 1.5)));
    const offset = seed * 0.000003 + index * 2.25;
    for (let i = 0; i <= count; i++) {
      const u = i / count;
      const theta = u * Math.PI * (2.1 + index * 0.35) + offset + phase * (index % 2 ? -0.7 : 0.8);
      const center = height * (0.5 + Math.sin(theta) * (0.21 + energy[0] * 0.1));
      const twist = Math.cos(theta * 0.8 + phase * 0.32);
      const thickness = height * (0.1 + 0.22 * Math.abs(twist)) * (0.8 + energy[1] * 0.26);
      const x = -width * 0.08 + u * width * 1.16;
      points.push({ x, top: center - thickness, bottom: center + thickness, twist });
    }
    // Clip all overlapping light strips to one continuous silhouette. Without
    // this, antialias overlap creates tiny stair steps along sloped edges.
    context.save();
    context.beginPath();
    context.moveTo(points[0].x, points[0].top);
    for (let i = 1; i <= count; i++) context.lineTo(points[i].x, points[i].top);
    for (let i = count; i >= 0; i--) context.lineTo(points[i].x, points[i].bottom);
    context.closePath();
    context.clip();
    // Dense strips give the curved surface local reflected light, with overlap
    // hidden by the shared silhouette and no exposed seams between slices.
    for (let i = 0; i < count; i++) {
      const a = points[i], b = points[i + 1];
      const gloss = context.createLinearGradient(a.x, a.top, a.x, a.bottom);
      const shine = 0.24 + 0.24 * (1 + a.twist) / 2;
      gloss.addColorStop(0, '#25282b');
      gloss.addColorStop(0.1, palette[index]);
      gloss.addColorStop(shine, '#f5f1e8');
      gloss.addColorStop(Math.min(0.85, shine + 0.13 + energy[2] * 0.08), palette[(index + 1) % 3]);
      gloss.addColorStop(0.92, '#454449');
      gloss.addColorStop(1, '#1b1c21');
      context.fillStyle = gloss;
      context.beginPath();
      context.moveTo(a.x - 0.5, a.top);
      context.lineTo(b.x + 0.5, b.top);
      context.lineTo(b.x + 0.5, b.bottom);
      context.lineTo(a.x - 0.5, a.bottom);
      context.closePath();
      context.fill();
    }
    context.restore();
  }
  return {
    // Call from the app's RAF. Identity is a stable track ID or combined A/B IDs.
    draw(analyser, identity = '', isPlaying = false) {
      if (!context) return;
      const now = performance.now();
      const nextKey = String(identity);
      const changed = nextKey !== identityKey;
      if (changed) {
        identityKey = nextKey;
        seed = hash(nextKey);
        palette = palettes[seed % palettes.length];
        phase = (seed % 1000) / 100;
        energy = [0, 0, 0];
      }
      const nextWidth = Math.round(canvas.clientWidth);
      const nextHeight = Math.round(canvas.clientHeight);
      const nextScale = Math.min(window.devicePixelRatio || 1, 1.5);
      if (!nextWidth || !nextHeight) return;
      const resized = nextWidth !== width || nextHeight !== height || nextScale !== scale;
      if (resized) {
        width = nextWidth; height = nextHeight; scale = nextScale;
        canvas.width = Math.round(width * scale);
        canvas.height = Math.round(height * scale);
      }
      const animate = isPlaying && !reducedMotion.matches;
      if (rendered && !changed && !resized && (!animate || now - lastDraw < 1000 / 30)) return;
      const elapsed = Math.min(0.05, Math.max(0, (now - lastDraw) / 1000));
      lastDraw = now;
      if (animate) {
        const target = spectrum(analyser);
        energy = energy.map((value, i) => value + (target[i] - value) * 0.13);
        phase += elapsed * (0.13 + energy[0] * 0.23);
      }
      context.setTransform(scale, 0, 0, scale, 0, 0);
      context.fillStyle = '#151619';
      context.fillRect(0, 0, width, height);
      const atmosphere = context.createLinearGradient(0, 0, width, height);
      atmosphere.addColorStop(0, palette[0] + '25');
      atmosphere.addColorStop(0.5, '#15161900');
      atmosphere.addColorStop(1, palette[2] + '25');
      context.fillStyle = atmosphere;
      context.fillRect(0, 0, width, height);
      for (let index = 2; index >= 0; index--) ribbon(index);
      rendered = true;
    },
  };
}
