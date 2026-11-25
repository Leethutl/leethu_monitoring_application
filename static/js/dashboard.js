(() => {
  const REFRESH_MS = 5000;

  async function refresh() {
    try {
      const res = await fetch("/api/metrics", { credentials: "same-origin" });
      if (!res.ok) return;
      const data = await res.json();
      for (const item of data.servers || []) {
        const card = document.querySelector(
          `.server-card[data-server-id="${item.server.id}"]`
        );
        if (!card) continue;
        const m = item.metrics;
        const cpu = card.querySelector('[data-metric="cpu"]');
        const mem = card.querySelector('[data-metric="mem"]');
        const disk = card.querySelector('[data-metric="disk"]');
        if (cpu) cpu.textContent = `${m.cpu_percent}%`;
        if (mem) mem.textContent = `${m.memory.percent}%`;
        if (disk) disk.textContent = `${m.disk_percent}%`;
      }
    } catch (_) {
      /* ignore transient network errors for demo refresh */
    }
  }

  setInterval(refresh, REFRESH_MS);
})();
