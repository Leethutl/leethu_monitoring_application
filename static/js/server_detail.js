(() => {
  const REFRESH_MS = 5000;
  const panel = document.getElementById("detail-metrics");
  if (!panel || typeof Chart === "undefined") return;

  const serverId = panel.dataset.serverId;
  const history = Array.isArray(window.__LEETHU_HISTORY__)
    ? window.__LEETHU_HISTORY__
    : [];

  const chartOpts = {
    responsive: true,
    animation: false,
    scales: {
      x: {
        ticks: { color: "#8b9aab", maxTicksLimit: 6 },
        grid: { color: "rgba(42,53,68,0.6)" },
      },
      y: {
        ticks: { color: "#8b9aab" },
        grid: { color: "rgba(42,53,68,0.6)" },
        beginAtZero: true,
      },
    },
    plugins: {
      legend: { labels: { color: "#e8eef4" } },
    },
  };

  function labelsFrom(points) {
    return points.map((p) => {
      const d = new Date((p.ts || 0) * 1000);
      return d.toLocaleTimeString([], { minute: "2-digit", second: "2-digit" });
    });
  }

  function makeChart(canvasId, label, color, values) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    return new Chart(ctx, {
      type: "line",
      data: {
        labels: labelsFrom(history),
        datasets: [
          {
            label,
            data: values,
            borderColor: color,
            backgroundColor: color + "33",
            tension: 0.25,
            fill: true,
            pointRadius: 0,
          },
        ],
      },
      options: chartOpts,
    });
  }

  const cpuChart = makeChart(
    "chart-cpu",
    "CPU %",
    "#2dd4bf",
    history.map((p) => p.cpu_percent)
  );
  const memChart = makeChart(
    "chart-memory",
    "Memory %",
    "#38bdf8",
    history.map((p) => p.memory_percent)
  );
  const netChart = (() => {
    const ctx = document.getElementById("chart-network");
    if (!ctx) return null;
    return new Chart(ctx, {
      type: "line",
      data: {
        labels: labelsFrom(history),
        datasets: [
          {
            label: "RX Mbps",
            data: history.map((p) => p.network_rx_mbps),
            borderColor: "#2dd4bf",
            tension: 0.25,
            pointRadius: 0,
          },
          {
            label: "TX Mbps",
            data: history.map((p) => p.network_tx_mbps),
            borderColor: "#fbbf24",
            tension: 0.25,
            pointRadius: 0,
          },
        ],
      },
      options: chartOpts,
    });
  })();
  const diskChart = makeChart(
    "chart-disk",
    "Disk %",
    "#a78bfa",
    history.map((p) => p.disk_percent)
  );

  function updateCharts(points) {
    const labs = labelsFrom(points);
    if (cpuChart) {
      cpuChart.data.labels = labs;
      cpuChart.data.datasets[0].data = points.map((p) => p.cpu_percent);
      cpuChart.update();
    }
    if (memChart) {
      memChart.data.labels = labs;
      memChart.data.datasets[0].data = points.map((p) => p.memory_percent);
      memChart.update();
    }
    if (netChart) {
      netChart.data.labels = labs;
      netChart.data.datasets[0].data = points.map((p) => p.network_rx_mbps);
      netChart.data.datasets[1].data = points.map((p) => p.network_tx_mbps);
      netChart.update();
    }
    if (diskChart) {
      diskChart.data.labels = labs;
      diskChart.data.datasets[0].data = points.map((p) => p.disk_percent);
      diskChart.update();
    }
  }

  function updateFields(m) {
    const set = (field, text) => {
      const el = panel.querySelector(`[data-field="${field}"]`);
      if (el) el.textContent = text;
    };
    set("cpu_percent", `${m.cpu_percent}%`);
    set("memory_percent", `${m.memory.percent}%`);
    set(
      "memory_detail",
      `${m.memory.used_gb} / ${m.memory.total_gb} GiB`
    );
    set("disk_percent", `${m.disk_percent}%`);
    set(
      "network",
      `↓ ${m.network.rx_mbps} / ↑ ${m.network.tx_mbps} Mbps`
    );
    set(
      "load_avg",
      `${m.load_avg[0]} · ${m.load_avg[1]} · ${m.load_avg[2]}`
    );
    set("uptime_human", m.uptime_human);

    const tbody = document.querySelector("#ports-table tbody");
    if (tbody && Array.isArray(m.ports)) {
      tbody.innerHTML = m.ports
        .map(
          (p) =>
            `<tr><td class="mono">${p.port}</td><td class="mono">${p.proto}</td><td class="mono">${p.process}</td></tr>`
        )
        .join("");
    }
  }

  async function refresh() {
    try {
      const res = await fetch(`/api/metrics/${serverId}`, {
        credentials: "same-origin",
      });
      if (!res.ok) return;
      const data = await res.json();
      updateFields(data.metrics);
      updateCharts(data.history || []);
    } catch (_) {
      /* ignore */
    }
  }

  setInterval(refresh, REFRESH_MS);
})();
