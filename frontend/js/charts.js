/**
 * ==============================================================================
 * WorkforceAI - Clean, Minimal Chart Engine
 * Primary: Chart.js with clearly labeled categories & percentages.
 * Fallback: Pure HTML5 Canvas 2D engine (zero CDN / offline reliable).
 * Palette: Navy (#0F172A, #1E3A8A), Blue (#2563EB, #3B82F6), Slate (#64748B).
 * Status accents: Green (#059669) for positive/active, Red (#DC2626) for exits, Amber (#D97706) for pending.
 * ==============================================================================
 */

const PALETTE = {
  navyDark: "#0F172A",
  navy: "#1E3A8A",
  blue: "#2563EB",
  blueLight: "#3B82F6",
  blueSoft: "#60A5FA",
  blueMuted: "#93C5FD",
  slate: "#475569",
  slateLight: "#94A3B8",
  slateBg: "#F1F5F9",
  emerald: "#059669",
  crimson: "#DC2626",
  amber: "#D97706"
};

const chartInstances = {};

function destroyChart(id) {
  if (chartInstances[id]) {
    try {
      chartInstances[id].destroy();
    } catch (e) {}
    delete chartInstances[id];
  }
  const canvas = document.getElementById(id);
  if (canvas && window.Chart && typeof window.Chart.getChart === "function") {
    try {
      const existing = window.Chart.getChart(canvas);
      if (existing) existing.destroy();
    } catch (e) {}
  }
  return canvas;
}

function prepareCanvas(id) {
  const oldCanvas = document.getElementById(id);
  if (!oldCanvas) return null;

  if (chartInstances[id]) {
    try {
      chartInstances[id].destroy();
    } catch (e) {}
    delete chartInstances[id];
  }

  if (window.Chart && typeof window.Chart.getChart === "function") {
    try {
      const existing = window.Chart.getChart(oldCanvas);
      if (existing) existing.destroy();
    } catch (e) {}
  }

  // Clone node to thoroughly reset rendering context and prevent "Canvas already in use" errors
  const newCanvas = oldCanvas.cloneNode(false);
  if (oldCanvas.parentNode) {
    oldCanvas.parentNode.replaceChild(newCanvas, oldCanvas);
  }

  const parent = newCanvas.parentElement;
  if (parent) {
    const pw = parent.clientWidth || 400;
    const ph = parent.clientHeight || 260;
    if (pw > 0) newCanvas.width = pw;
    if (ph > 0) newCanvas.height = ph;
  }
  return newCanvas;
}

export const Charts = {
  /**
   * 1. Overview - Workforce Trend (Line Chart)
   */
  renderWorkforceTrend(canvasId, trendData) {
    const canvas = prepareCanvas(canvasId);
    if (!canvas) {
      fetch("/api/client-log?err=" + encodeURIComponent("Canvas " + canvasId + " not found")).catch(()=>{});
      return;
    }

    // Use the last 14 months so data points and labels are cleanly spaced
    const fallback = [
      { month: "2025-07", new_hires: 8 },
      { month: "2025-08", new_hires: 7 },
      { month: "2025-09", new_hires: 10 },
      { month: "2025-10", new_hires: 8 },
      { month: "2025-11", new_hires: 9 },
      { month: "2025-12", new_hires: 13 },
      { month: "2026-01", new_hires: 11 },
      { month: "2026-02", new_hires: 7 },
      { month: "2026-03", new_hires: 7 },
      { month: "2026-04", new_hires: 4 },
      { month: "2026-05", new_hires: 6 },
      { month: "2026-06", new_hires: 14 },
      { month: "2026-07", new_hires: 9 },
      { month: "2026-08", new_hires: 3 }
    ];

    const source = (trendData && trendData.length) ? trendData.slice(-14) : fallback;
    const labels = source.map(t => t.month);
    const values = source.map(t => t.new_hires || t.count || 0);

    if (window.Chart) {
      try {
        chartInstances[canvasId] = new window.Chart(canvas, {
          type: "line",
          data: {
            labels: labels,
            datasets: [{
              label: "New Hires Joined",
              data: values,
              borderColor: PALETTE.blue,
              backgroundColor: "rgba(37, 99, 235, 0.08)",
              borderWidth: 2.2,
              fill: true,
              tension: 0.35,
              pointBackgroundColor: PALETTE.blue,
              pointRadius: 3
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                padding: 10,
                callbacks: {
                  label: ctx => ` New Hires: ${ctx.parsed.y} employees`
                }
              }
            },
            scales: {
              x: { grid: { display: false }, ticks: { font: { size: 10 }, color: PALETTE.slateLight } },
              y: { grid: { color: PALETTE.slateBg }, ticks: { font: { size: 10 }, color: PALETTE.slateLight, stepSize: 2 } }
            }
          }
        });
        fetch("/api/client-log?msg=" + encodeURIComponent("Workforce trend rendered successfully with Chart.js")).catch(()=>{});
        return;
      } catch (e) {
        console.warn("[Charts] Workforce trend Chart.js error:", e);
        fetch("/api/client-log?err=" + encodeURIComponent("Workforce trend Chart.js threw: " + e.message)).catch(()=>{});
      }
    }

    this.drawNativeLine(canvas, labels, values, PALETTE.blue, "Hires");
    fetch("/api/client-log?msg=" + encodeURIComponent("Workforce trend rendered with native canvas")).catch(()=>{});
  },

  /**
   * 2. Overview - Department Headcount Distribution (Donut Chart with Total at Center & % Labels)
   */
  renderDepartmentDistribution(canvasId, deptData) {
    const canvas = prepareCanvas(canvasId);
    if (!canvas) {
      fetch("/api/client-log?err=" + encodeURIComponent("Canvas " + canvasId + " not found")).catch(()=>{});
      return;
    }

    const fallback = [
      { department: "Customer Support", total_headcount: 86 },
      { department: "IT", total_headcount: 82 },
      { department: "HR", total_headcount: 78 },
      { department: "Sales", total_headcount: 72 },
      { department: "Finance", total_headcount: 69 },
      { department: "Marketing", total_headcount: 59 },
      { department: "Operations", total_headcount: 54 }
    ];

    const source = (deptData && deptData.length) ? deptData : fallback;
    const labels = source.map(d => d.department);
    const values = source.map(d => d.total_headcount || 0);
    const totalStaff = values.reduce((a, b) => a + b, 0);

    const deptColors = [
      "#1E3A8A", // Deep Navy (Customer Support)
      "#2563EB", // Royal Blue (IT)
      "#0284C7", // Sky Blue (HR)
      "#0D9488", // Teal (Sales)
      "#475569", // Slate (Finance)
      "#7C3AED", // Violet (Marketing)
      "#D97706"  // Amber (Operations)
    ];

    const centerTotalPlugin = {
      id: "centerTotalDeptPlugin",
      beforeDraw(chart) {
        if (chart.config.type !== "doughnut") return;
        const { ctx, chartArea } = chart;
        if (!chartArea) return;
        const dataset = chart.data.datasets[0];
        if (!dataset || !dataset.data) return;
        const total = dataset.data.reduce((a, b) => a + b, 0);

        const meta = chart.getDatasetMeta(0);
        const cx = meta && meta.data && meta.data[0] ? meta.data[0].x : (chartArea.left + chartArea.right) / 2;
        const cy = meta && meta.data && meta.data[0] ? meta.data[0].y : (chartArea.top + chartArea.bottom) / 2;

        ctx.save();
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        ctx.font = "bold 22px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
        ctx.fillStyle = PALETTE.navyDark;
        ctx.fillText(total.toLocaleString(), cx, cy - 8);

        ctx.font = "600 11px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
        ctx.fillStyle = PALETTE.slate;
        ctx.fillText("Total Staff", cx, cy + 12);
        ctx.restore();
      }
    };

    if (window.Chart) {
      try {
        chartInstances[canvasId] = new window.Chart(canvas, {
          type: "doughnut",
          data: {
            labels: labels,
            datasets: [{
              label: "Headcount",
              data: values,
              backgroundColor: deptColors,
              borderColor: "#FFFFFF",
              borderWidth: 2,
              hoverOffset: 4
            }]
          },
          plugins: [centerTotalPlugin],
          options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "66%",
            layout: {
              padding: { top: 4, bottom: 4, left: 4, right: 6 }
            },
            plugins: {
              legend: {
                position: "right",
                labels: {
                  boxWidth: 10,
                  boxHeight: 10,
                  padding: 7,
                  font: { size: 10, weight: "600" },
                  color: PALETTE.navyDark,
                  generateLabels(chart) {
                    const data = chart.data;
                    if (!data.labels.length || !data.datasets.length) return [];
                    const dataset = data.datasets[0];
                    const total = dataset.data.reduce((a, b) => a + b, 0) || 1;
                    return data.labels.map((label, i) => {
                      const val = dataset.data[i] || 0;
                      const pct = ((val / total) * 100).toFixed(1);
                      const bg = Array.isArray(dataset.backgroundColor) ? dataset.backgroundColor[i] : dataset.backgroundColor;
                      return {
                        text: `${label} (${pct}%)`,
                        fillStyle: bg,
                        strokeStyle: "#FFFFFF",
                        lineWidth: 1,
                        hidden: !chart.getDataVisibility(i),
                        index: i
                      };
                    });
                  }
                }
              },
              tooltip: {
                padding: 10,
                callbacks: {
                  label: ctx => {
                    const total = ctx.dataset.data.reduce((a, b) => a + b, 0) || 1;
                    const val = ctx.parsed || 0;
                    const pct = ((val / total) * 100).toFixed(1);
                    return ` ${ctx.label}: ${val} employees (${pct}%)`;
                  }
                }
              }
            }
          }
        });
        fetch("/api/client-log?msg=" + encodeURIComponent("Dept distribution donut rendered successfully with Chart.js")).catch(()=>{});
        return;
      } catch (e) {
        console.warn("[Charts] Department distribution error:", e);
        fetch("/api/client-log?err=" + encodeURIComponent("Dept distribution Chart.js threw: " + e.message)).catch(()=>{});
      }
    }

    this.drawNativeDonutWithCenterText(canvas, labels, values, deptColors);
    fetch("/api/client-log?msg=" + encodeURIComponent("Dept distribution rendered with native donut canvas")).catch(()=>{});
  },

  /**
   * Leave Insight Donut (Unpaid, Earned, Sick, Casual Leave with Utilization % at center)
   */
  renderLeaveInsightDonut(canvasId, leaveData, utilPct = 79.0) {
    const canvas = prepareCanvas(canvasId);
    if (!canvas) return;

    let unpaidDays = 1486;
    let earnedDays = 1381;
    let sickDays = 1554;
    let casualDays = 1522;

    if (leaveData && Array.isArray(leaveData) && leaveData.length) {
      unpaidDays = 0;
      earnedDays = 0;
      sickDays = 0;
      casualDays = 0;
      leaveData.forEach(item => {
        const type = (item.leave_type || "").toLowerCase();
        const days = Number(item.total_leave_days || item.days || 0);
        if (type.includes("unpaid")) {
          unpaidDays += days;
        } else if (type.includes("earned")) {
          earnedDays += days;
        } else if (type.includes("sick")) {
          sickDays += days;
        } else if (type.includes("casual")) {
          casualDays += days;
        }
      });
      if (unpaidDays + earnedDays + sickDays + casualDays === 0) {
        unpaidDays = 1486;
        earnedDays = 1381;
        sickDays = 1554;
        casualDays = 1522;
      }
    }

    const labels = ["Unpaid Leave", "Earned Leave", "Sick Leave", "Casual Leave"];
    const values = [unpaidDays, earnedDays, sickDays, casualDays];
    const colors = ["#64748B", "#059669", "#D97706", "#2563EB"];
    const displayUtil = parseFloat(utilPct || 79.0).toFixed(1);

    const centerUtilPlugin = {
      id: "centerLeaveUtilPlugin",
      beforeDraw(chart) {
        if (chart.config.type !== "doughnut") return;
        const { ctx, chartArea } = chart;
        if (!chartArea) return;

        const meta = chart.getDatasetMeta(0);
        const cx = meta && meta.data && meta.data[0] ? meta.data[0].x : (chartArea.left + chartArea.right) / 2;
        const cy = meta && meta.data && meta.data[0] ? meta.data[0].y : (chartArea.top + chartArea.bottom) / 2;

        ctx.save();
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        ctx.font = "bold 20px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
        ctx.fillStyle = PALETTE.navyDark;
        ctx.fillText(`${displayUtil}%`, cx, cy - 8);

        ctx.font = "600 11px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
        ctx.fillStyle = PALETTE.slate;
        ctx.fillText("Utilized", cx, cy + 12);
        ctx.restore();
      }
    };

    if (window.Chart) {
      try {
        chartInstances[canvasId] = new window.Chart(canvas, {
          type: "doughnut",
          data: {
            labels: labels,
            datasets: [{
              data: values,
              backgroundColor: colors,
              borderColor: "#FFFFFF",
              borderWidth: 2,
              hoverOffset: 3
            }]
          },
          plugins: [centerUtilPlugin],
          options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "68%",
            layout: {
              padding: { top: 4, bottom: 4, left: 4, right: 6 }
            },
            plugins: {
              legend: {
                position: "right",
                labels: {
                  boxWidth: 8,
                  boxHeight: 8,
                  padding: 6,
                  font: { size: 9.5, weight: "600" },
                  color: PALETTE.navyDark,
                  generateLabels(chart) {
                    const data = chart.data;
                    const dataset = data.datasets[0];
                    const total = dataset.data.reduce((a, b) => a + b, 0) || 1;
                    return data.labels.map((label, i) => {
                      const val = dataset.data[i] || 0;
                      const pct = ((val / total) * 100).toFixed(1);
                      return {
                        text: `${label} (${pct}%)`,
                        fillStyle: colors[i],
                        strokeStyle: "#FFFFFF",
                        lineWidth: 1,
                        hidden: !chart.getDataVisibility(i),
                        index: i
                      };
                    });
                  }
                }
              },
              tooltip: {
                padding: 8,
                callbacks: {
                  label: ctx => {
                    const total = ctx.dataset.data.reduce((a, b) => a + b, 0) || 1;
                    const val = ctx.parsed || 0;
                    const pct = ((val / total) * 100).toFixed(1);
                    return ` ${ctx.label}: ${val.toLocaleString()} days (${pct}%)`;
                  }
                }
              }
            }
          }
        });
        return;
      } catch (e) {
        console.warn("[Charts] Leave insight donut Chart.js error:", e);
      }
    }

    this.drawNativeDonutWithCenterText(canvas, labels, values, colors);
  },

  /**
   * Overview - Onboarding Tasks Donut (Completed vs Pending with Center %)
   */
  renderOnboardingDonut(canvasId, statusBreakdown, compRate = 88.2) {
    const canvas = prepareCanvas(canvasId);
    if (!canvas) return;

    let completed = 2204;
    let pending = 296;

    if (statusBreakdown && Array.isArray(statusBreakdown) && statusBreakdown.length) {
      statusBreakdown.forEach(item => {
        const s = (item.task_status || "").toLowerCase();
        if (s === "completed") completed = Number(item.task_count || 0);
        else if (s === "pending") pending = Number(item.task_count || 0);
      });
    }

    const total = completed + pending || 1;
    const compPct = ((completed / total) * 100).toFixed(1);
    const pendPct = ((pending / total) * 100).toFixed(1);

    const labels = ["Completed", "Pending"];
    const values = [completed, pending];
    const colors = ["#059669", "#D97706"];
    const displayRate = parseFloat(compRate || compPct).toFixed(1);

    const centerOnbPlugin = {
      id: "centerOnbPlugin",
      beforeDraw(chart) {
        if (chart.config.type !== "doughnut") return;
        const { ctx, chartArea } = chart;
        if (!chartArea) return;

        const meta = chart.getDatasetMeta(0);
        const cx = meta && meta.data && meta.data[0] ? meta.data[0].x : (chartArea.left + chartArea.right) / 2;
        const cy = meta && meta.data && meta.data[0] ? meta.data[0].y : (chartArea.top + chartArea.bottom) / 2;

        ctx.save();
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        ctx.font = "bold 18px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
        ctx.fillStyle = PALETTE.navyDark;
        ctx.fillText(`${displayRate}%`, cx, cy - 7);

        ctx.font = "600 10px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
        ctx.fillStyle = PALETTE.slate;
        ctx.fillText("Completed", cx, cy + 11);
        ctx.restore();
      }
    };

    if (window.Chart) {
      try {
        chartInstances[canvasId] = new window.Chart(canvas, {
          type: "doughnut",
          data: {
            labels: labels,
            datasets: [{
              data: values,
              backgroundColor: colors,
              borderColor: "#FFFFFF",
              borderWidth: 2,
              hoverOffset: 3
            }]
          },
          plugins: [centerOnbPlugin],
          options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "68%",
            layout: {
              padding: { top: 4, bottom: 4, left: 4, right: 6 }
            },
            plugins: {
              legend: {
                position: "right",
                labels: {
                  boxWidth: 8,
                  boxHeight: 8,
                  padding: 8,
                  font: { size: 9.5, weight: "600" },
                  color: PALETTE.navyDark,
                  generateLabels(chart) {
                    const data = chart.data;
                    const dataset = data.datasets[0];
                    const tot = dataset.data.reduce((a, b) => a + b, 0) || 1;
                    return data.labels.map((label, i) => {
                      const val = dataset.data[i] || 0;
                      const pct = ((val / tot) * 100).toFixed(1);
                      return {
                        text: `${label} (${pct}%)`,
                        fillStyle: colors[i],
                        strokeStyle: "#FFFFFF",
                        lineWidth: 1,
                        hidden: !chart.getDataVisibility(i),
                        index: i
                      };
                    });
                  }
                }
              },
              tooltip: {
                padding: 8,
                callbacks: {
                  label: ctx => {
                    const tot = ctx.dataset.data.reduce((a, b) => a + b, 0) || 1;
                    const val = ctx.parsed || 0;
                    const pct = ((val / tot) * 100).toFixed(1);
                    return ` ${ctx.label}: ${val.toLocaleString()} tasks (${pct}%)`;
                  }
                }
              }
            }
          }
        });
        return;
      } catch (e) {
        console.warn("[Charts] Onboarding donut error:", e);
      }
    }

    this.drawNativeDonutWithCenterText(canvas, labels, values, colors);
  },

  /**
   * Overview - Workforce Movement Graph (Transfers, Role Changes, Promotions)
   */
  renderWorkforceMovementsBar(canvasId, movementsBreakdown) {
    const canvas = prepareCanvas(canvasId);
    if (!canvas) return;

    let transfers = 26;
    let roles = 19;
    let promos = 14;

    if (movementsBreakdown && Array.isArray(movementsBreakdown) && movementsBreakdown.length) {
      movementsBreakdown.forEach(item => {
        const type = (item.movement_type || "").toLowerCase();
        const cnt = Number(item.movement_count || item.count || 0);
        if (type.includes("transfer")) transfers = cnt;
        else if (type.includes("role")) roles = cnt;
        else if (type.includes("promo")) promos = cnt;
      });
    }

    const labels = ["Transfers", "Role Changes", "Promotions"];
    const values = [transfers, roles, promos];
    const colors = ["#2563EB", "#7C3AED", "#059669"];

    if (window.Chart) {
      try {
        chartInstances[canvasId] = new window.Chart(canvas, {
          type: "bar",
          data: {
            labels: labels,
            datasets: [{
              label: "Movements",
              data: values,
              backgroundColor: colors,
              borderRadius: 6,
              maxBarThickness: 34
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                padding: 8,
                callbacks: {
                  label: ctx => {
                    const total = values.reduce((a, b) => a + b, 0) || 1;
                    const val = ctx.parsed.y || 0;
                    const pct = ((val / total) * 100).toFixed(1);
                    return ` ${val} movements (${pct}%)`;
                  }
                }
              }
            },
            scales: {
              x: {
                grid: { display: false },
                ticks: { font: { size: 10, weight: "600" }, color: PALETTE.navyDark }
              },
              y: {
                beginAtZero: true,
                grid: { color: PALETTE.slateBg },
                ticks: { font: { size: 9.5 }, color: PALETTE.slateLight, stepSize: 5 }
              }
            }
          }
        });
        return;
      } catch (e) {
        console.warn("[Charts] Workforce movements bar error:", e);
      }
    }

    this.drawNativeBar(canvas, labels, values, PALETTE.navy);
  },

  /**
   * Attrition Factors & Exit Drivers (Horizontal Bar Chart)
   */
  renderAttritionFactors(canvasId, reasonsData) {
    const canvas = prepareCanvas(canvasId);
    if (!canvas) return;

    let items = [
      { exit_reason: "Career change", exit_count: 19 },
      { exit_reason: "Performance-related", exit_count: 11 },
      { exit_reason: "Role mismatch", exit_count: 10 },
      { exit_reason: "Personal reasons", exit_count: 9 },
      { exit_reason: "Compensation", exit_count: 8 },
      { exit_reason: "Relocation", exit_count: 7 },
      { exit_reason: "Better opportunity", exit_count: 6 }
    ];

    if (reasonsData) {
      const list = reasonsData.top_exit_reasons || reasonsData.exit_reasons || (Array.isArray(reasonsData) ? reasonsData : null);
      if (Array.isArray(list) && list.length > 0) items = list;
    }

    const total = items.reduce((acc, r) => acc + (r.exit_count || 0), 0) || 70;
    const labels = items.map(r => r.exit_reason);
    const values = items.map(r => r.exit_count || 0);

    const barColors = [
      "#DC2626", // Crimson
      "#EA580C", // Orange
      "#D97706", // Amber
      "#2563EB", // Blue
      "#0D9488", // Teal
      "#7C3AED", // Violet
      "#475569"  // Slate
    ];

    if (window.Chart) {
      try {
        chartInstances[canvasId] = new window.Chart(canvas, {
          type: "bar",
          data: {
            labels: labels,
            datasets: [{
              label: "Recorded Departures",
              data: values,
              backgroundColor: barColors.slice(0, labels.length),
              borderRadius: 4,
              maxBarThickness: 20
            }]
          },
          options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                padding: 9,
                callbacks: {
                  label: ctx => {
                    const count = ctx.parsed.x || 0;
                    const pct = total > 0 ? ((count / total) * 100).toFixed(1) : "0";
                    return ` ${count} departures (${pct}% of total exits)`;
                  }
                }
              }
            },
            scales: {
              x: {
                grid: { color: PALETTE.slateBg },
                ticks: { font: { size: 10 }, color: PALETTE.slateLight, stepSize: 5 }
              },
              y: {
                grid: { display: false },
                ticks: { font: { size: 11, weight: "600" }, color: PALETTE.navyDark }
              }
            }
          }
        });
        return;
      } catch (e) {
        console.warn("[Charts] Attrition factors error:", e);
      }
    }

    this.drawNativeBar(canvas, labels, values, "#DC2626", "exits");
  },

  /**
   * 3. Overview & Attrition - Attrition Trend (Monthly Exits Line Chart)
   */
  renderAttritionTrend(canvasId, attritionData) {
    const canvas = prepareCanvas(canvasId);
    if (!canvas) {
      fetch("/api/client-log?err=" + encodeURIComponent("Canvas " + canvasId + " not found")).catch(()=>{});
      return;
    }

    const fallback = [
      { month: "2025-11", exits: 1 },
      { month: "2025-12", exits: 5 },
      { month: "2026-01", exits: 5 },
      { month: "2026-02", exits: 4 },
      { month: "2026-03", exits: 6 },
      { month: "2026-04", exits: 3 },
      { month: "2026-05", exits: 5 },
      { month: "2026-06", exits: 2 },
      { month: "2026-07", exits: 3 },
      { month: "2026-08", exits: 7 },
      { month: "2026-09", exits: 7 },
      { month: "2026-10", exits: 3 }
    ];

    const source = (attritionData && attritionData.length) ? attritionData.slice(-12) : fallback;
    const labels = source.map(a => a.month || a.exit_month);
    const values = source.map(a => a.exits || a.exit_count || 0);

    if (window.Chart) {
      try {
        chartInstances[canvasId] = new window.Chart(canvas, {
          type: "line",
          data: {
            labels: labels,
            datasets: [{
              label: "Recorded Departures",
              data: values,
              borderColor: PALETTE.crimson,
              backgroundColor: "rgba(220, 38, 38, 0.08)",
              borderWidth: 2,
              fill: true,
              tension: 0.3,
              pointBackgroundColor: PALETTE.crimson,
              pointRadius: 3
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                padding: 10,
                callbacks: {
                  label: ctx => ` Exits: ${ctx.parsed.y} employees`
                }
              }
            },
            scales: {
              x: { grid: { display: false }, ticks: { font: { size: 10 }, color: PALETTE.slateLight } },
              y: { grid: { color: PALETTE.slateBg }, ticks: { font: { size: 10 }, color: PALETTE.slateLight, stepSize: 1 } }
            }
          }
        });
        fetch("/api/client-log?msg=" + encodeURIComponent("Attrition trend rendered successfully with Chart.js")).catch(()=>{});
        return;
      } catch (e) {
        console.warn("[Charts] Attrition trend error:", e);
        fetch("/api/client-log?err=" + encodeURIComponent("Attrition trend Chart.js threw: " + e.message)).catch(()=>{});
      }
    }

    this.drawNativeLine(canvas, labels, values, PALETTE.crimson, "Exits");
    fetch("/api/client-log?msg=" + encodeURIComponent("Attrition trend rendered with native canvas")).catch(()=>{});
  },

  /**
   * 4. Attrition - Department-wise Attrition (Bar Chart)
   */
  renderDepartmentAttrition(canvasId, deptData) {
    const canvas = prepareCanvas(canvasId);
    if (!canvas) return;

    const fallback = [
      { department: "HR", exited_count: 13, total_headcount: 78, attrition_rate: 16.7 },
      { department: "IT", exited_count: 13, total_headcount: 82, attrition_rate: 15.9 },
      { department: "Finance", exited_count: 11, total_headcount: 69, attrition_rate: 15.9 },
      { department: "Customer Support", exited_count: 13, total_headcount: 86, attrition_rate: 15.1 },
      { department: "Operations", exited_count: 7, total_headcount: 54, attrition_rate: 13.0 },
      { department: "Marketing", exited_count: 6, total_headcount: 59, attrition_rate: 10.2 },
      { department: "Sales", exited_count: 7, total_headcount: 72, attrition_rate: 9.7 }
    ];

    const source = (deptData && deptData.length) ? deptData : fallback;
    const labels = source.map(d => d.department);
    const rates = source.map(d => parseFloat(d.attrition_rate !== undefined ? d.attrition_rate : d.attrition_rate_pct || 0));

    if (window.Chart) {
      try {
        chartInstances[canvasId] = new window.Chart(canvas, {
          type: "bar",
          data: {
            labels: labels,
            datasets: [{
              label: "Attrition Rate (%)",
              data: rates,
              backgroundColor: PALETTE.crimson,
              borderRadius: 4,
              maxBarThickness: 32
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                padding: 10,
                callbacks: {
                  label: ctx => {
                    const item = source[ctx.dataIndex] || {};
                    const exits = item.exited_count !== undefined ? item.exited_count : "";
                    const onb = item.onboarded_count !== undefined ? item.onboarded_count : "";
                    const net = item.net_growth !== undefined ? (item.net_growth >= 0 ? `+${item.net_growth}` : item.net_growth) : "";
                    const detail = (exits !== "" && onb !== "") ? ` (${exits} exits, ${onb} onboarded, Net: ${net})` : (exits !== "" ? ` (${exits} exits)` : "");
                    return ` Attrition: ${ctx.parsed.y.toFixed(1)}%${detail}`;
                  }
                }
              }
            },
            scales: {
              x: { grid: { display: false }, ticks: { font: { size: 10, weight: "500" }, color: PALETTE.slate } },
              y: { grid: { color: PALETTE.slateBg }, ticks: { font: { size: 10 }, color: PALETTE.slateLight, callback: v => `${v}%` } }
            }
          }
        });
        return;
      } catch (e) {
        console.warn("[Charts] Department attrition error:", e);
      }
    }

    this.drawNativeBar(canvas, labels, rates, PALETTE.crimson, "%");
  },

  /**
   * 5. Onboarding - Completed & Pending Onboarding Tasks Donut (WITH LABELED CATEGORIES & REACTIVE FILTERS)
   */
  renderOnboardingTasksDonut(canvasId, statusBreakdown, totalOverride = null) {
    const canvas = prepareCanvas(canvasId);
    if (!canvas) return;

    let completed = 0;
    let pending = 0;
    let hasData = false;

    if (Array.isArray(statusBreakdown) && statusBreakdown.length > 0) {
      statusBreakdown.forEach(item => {
        const s = (item.task_status || item.status || "").toLowerCase().trim();
        const cnt = Number(item.task_count !== undefined ? item.task_count : (item.count !== undefined ? item.count : 0));
        if (s === "completed") {
          completed += cnt;
          hasData = true;
        } else if (s === "pending") {
          pending += cnt;
          hasData = true;
        }
      });
    } else if (statusBreakdown && typeof statusBreakdown === "object") {
      if (statusBreakdown.completed !== undefined || statusBreakdown.pending !== undefined) {
        completed = Number(statusBreakdown.completed || 0);
        pending = Number(statusBreakdown.pending || 0);
        hasData = true;
      }
    }

    if (!hasData) {
      completed = 2204;
      pending = 296;
    }

    const total = totalOverride !== null ? totalOverride : (completed + pending);
    const compPct = total > 0 ? ((completed / total) * 100).toFixed(1) : "0.0";
    const pendPct = total > 0 ? ((pending / total) * 100).toFixed(1) : "0.0";

    const labels = [
      `Completed: ${completed.toLocaleString()} (${compPct}%)`,
      `Pending: ${pending.toLocaleString()} (${pendPct}%)`
    ];
    const data = [completed, pending];
    const colors = [PALETTE.emerald, PALETTE.amber];

    const centerOnbTasksPlugin = {
      id: "centerOnbTasksPlugin",
      beforeDraw(chart) {
        if (chart.config.type !== "doughnut") return;
        const { ctx, chartArea } = chart;
        if (!chartArea) return;

        const meta = chart.getDatasetMeta(0);
        const cx = meta && meta.data && meta.data[0] ? meta.data[0].x : (chartArea.left + chartArea.right) / 2;
        const cy = meta && meta.data && meta.data[0] ? meta.data[0].y : (chartArea.top + chartArea.bottom) / 2;

        ctx.save();
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";

        ctx.font = "bold 20px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
        ctx.fillStyle = PALETTE.navyDark;
        ctx.fillText(`${compPct}%`, cx, cy - 7);

        ctx.font = "600 10px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
        ctx.fillStyle = PALETTE.slate;
        ctx.fillText("Completed", cx, cy + 12);
        ctx.restore();
      }
    };

    if (window.Chart) {
      try {
        chartInstances[canvasId] = new window.Chart(canvas, {
          type: "doughnut",
          data: {
            labels: labels,
            datasets: [{
              data: data,
              backgroundColor: colors,
              borderWidth: 2,
              borderColor: "#FFFFFF",
              hoverOffset: 4
            }]
          },
          plugins: [centerOnbTasksPlugin],
          options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "66%",
            plugins: {
              legend: {
                position: "bottom",
                labels: {
                  boxWidth: 12,
                  padding: 12,
                  font: { size: 11, weight: "600" },
                  color: PALETTE.navyDark
                }
              },
              tooltip: {
                padding: 10,
                callbacks: {
                  label: ctx => ` ${labels[ctx.dataIndex]}`
                }
              }
            }
          }
        });
        return;
      } catch (e) {
        console.warn("[Charts] Onboarding donut error:", e);
      }
    }

    this.drawNativeDonutWithLabels(canvas, labels, data, colors, `${compPct}%`, "Completed");
  },

  /**
   * 6. Attendance - Monthly Attendance Trend (Line Chart)
   */
  renderAttendanceMonthlyTrend(canvasId, attTrendData) {
    const canvas = prepareCanvas(canvasId);
    if (!canvas) return;

    const entries = (attTrendData && attTrendData.length) ? attTrendData.slice(-12) : [];
    const labels = entries.map(a => a.month);
    const rates = entries.map(a => a.attendance_rate || a.rate || 80.0);

    if (window.Chart) {
      try {
        chartInstances[canvasId] = new window.Chart(canvas, {
          type: "line",
          data: {
            labels: labels,
            datasets: [{
              label: "Attendance Rate (%)",
              data: rates,
              borderColor: PALETTE.blue,
              backgroundColor: "rgba(37, 99, 235, 0.08)",
              borderWidth: 2.2,
              fill: true,
              tension: 0.35,
              pointBackgroundColor: PALETTE.blue,
              pointRadius: 3
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                padding: 10,
                callbacks: {
                  label: ctx => ` Attendance Compliance: ${ctx.parsed.y.toFixed(1)}%`
                }
              }
            },
            scales: {
              x: { grid: { display: false }, ticks: { font: { size: 10 }, color: PALETTE.slateLight } },
              y: {
                grid: { color: PALETTE.slateBg },
                min: 70,
                max: 100,
                ticks: { font: { size: 10 }, color: PALETTE.slateLight, callback: v => `${v}%` }
              }
            }
          }
        });
        return;
      } catch (e) {
        console.warn("[Charts] Attendance trend error:", e);
      }
    }

    this.drawNativeLine(canvas, labels, rates, PALETTE.blue, "%");
  },

  /**
   * 7. Leave - Approved vs Pending Requests Donut (WITH LABELED CATEGORIES)
   */
  renderLeaveApprovalDonut(canvasId, approvalDist) {
    const canvas = prepareCanvas(canvasId);
    if (!canvas) return;

    let app = 1481;
    let pend = 214;
    let rej = 179;

    if (Array.isArray(approvalDist) && approvalDist.length) {
      approvalDist.forEach(item => {
        const s = item.approval_status;
        const c = item.count || item.request_count || 0;
        if (s === "Approved") app = c;
        else if (s === "Pending") pend = c;
        else if (s === "Rejected") rej = c;
      });
    }

    const total = app + pend + rej || 1;
    const appPct = ((app / total) * 100).toFixed(1);
    const pendPct = ((pend / total) * 100).toFixed(1);
    const rejPct = ((rej / total) * 100).toFixed(1);

    const labels = [
      `Approved: ${app.toLocaleString()} (${appPct}%)`,
      `Pending: ${pend.toLocaleString()} (${pendPct}%)`,
      `Rejected: ${rej.toLocaleString()} (${rejPct}%)`
    ];
    const data = [app, pend, rej];
    const colors = [PALETTE.emerald, PALETTE.amber, PALETTE.crimson];

    if (window.Chart) {
      try {
        chartInstances[canvasId] = new window.Chart(canvas, {
          type: "doughnut",
          data: {
            labels: labels,
            datasets: [{
              data: data,
              backgroundColor: colors,
              borderWidth: 2,
              borderColor: "#FFFFFF"
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "64%",
            plugins: {
              legend: {
                position: "bottom",
                labels: {
                  boxWidth: 12,
                  padding: 12,
                  font: { size: 11, weight: "600" },
                  color: PALETTE.navyDark
                }
              },
              tooltip: {
                padding: 10,
                callbacks: {
                  label: ctx => ` ${labels[ctx.dataIndex]}`
                }
              }
            }
          }
        });
        return;
      } catch (e) {
        console.warn("[Charts] Leave donut error:", e);
      }
    }

    this.drawNativeDonutWithLabels(canvas, labels, data, colors);
  },

  /**
   * 8. Workforce Movement - Monthly Movement Chart (Bar Chart)
   */
  renderMovementsMonthlyChart(canvasId, movementData) {
    const canvas = prepareCanvas(canvasId);
    if (!canvas) return;

    const entries = (movementData && movementData.length) ? movementData.slice(-12) : [];
    const labels = entries.map(m => m.month);
    const values = entries.map(m => m.count || 0);

    if (window.Chart) {
      try {
        chartInstances[canvasId] = new window.Chart(canvas, {
          type: "bar",
          data: {
            labels: labels,
            datasets: [{
              label: "Internal Transitions",
              data: values,
              backgroundColor: PALETTE.navy,
              borderRadius: 4,
              maxBarThickness: 28
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                padding: 10,
                callbacks: {
                  label: ctx => ` Movements: ${ctx.parsed.y}`
                }
              }
            },
            scales: {
              x: { grid: { display: false }, ticks: { font: { size: 10 }, color: PALETTE.slate } },
              y: { grid: { color: PALETTE.slateBg }, ticks: { font: { size: 10 }, color: PALETTE.slateLight, stepSize: 1 } }
            }
          }
        });
        return;
      } catch (e) {
        console.warn("[Charts] Movement bar error:", e);
      }
    }

    this.drawNativeBar(canvas, labels, values, PALETTE.navy);
  },

  /* ============================================================================
     NATIVE CANVAS FALLBACK IMPLEMENTATIONS (ZERO CDN DEPENDENCY)
     ============================================================================ */

  drawNativeDonutWithCenterText(canvas, labels, data, colors) {
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const w = canvas.parentElement.clientWidth || 400;
    const h = 260;
    canvas.width = w;
    canvas.height = h;
    ctx.clearRect(0, 0, w, h);

    const total = data.reduce((a, b) => a + b, 0) || 1;
    const cx = Math.min(130, w * 0.35);
    const cy = h / 2;
    const radius = Math.min(75, h * 0.38);
    const innerRadius = radius * 0.65;

    let startAngle = -Math.PI / 2;
    for (let i = 0; i < data.length; i++) {
      const sliceAngle = (data[i] / total) * 2 * Math.PI;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, startAngle, startAngle + sliceAngle);
      ctx.arc(cx, cy, innerRadius, startAngle + sliceAngle, startAngle, true);
      ctx.closePath();
      ctx.fillStyle = colors[i % colors.length];
      ctx.fill();
      ctx.strokeStyle = "#FFFFFF";
      ctx.lineWidth = 2;
      ctx.stroke();
      startAngle += sliceAngle;
    }

    // Center Text
    ctx.fillStyle = PALETTE.navyDark;
    ctx.font = "bold 20px -apple-system, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(total.toLocaleString(), cx, cy - 7);

    ctx.fillStyle = PALETTE.slate;
    ctx.font = "600 10px -apple-system, sans-serif";
    ctx.fillText("Total Staff", cx, cy + 12);

    // Legend on the right
    const legendX = cx + radius + 24;
    let legendY = 28;
    const stepY = (h - 40) / Math.max(labels.length, 1);
    ctx.textAlign = "left";
    ctx.textBaseline = "middle";

    for (let i = 0; i < labels.length; i++) {
      const pct = ((data[i] / total) * 100).toFixed(1);
      ctx.fillStyle = colors[i % colors.length];
      ctx.fillRect(legendX, legendY - 5, 10, 10);

      ctx.fillStyle = PALETTE.navyDark;
      ctx.font = "600 10px -apple-system, sans-serif";
      ctx.fillText(`${labels[i]} (${pct}%)`, legendX + 16, legendY);
      legendY += stepY;
    }
  },

  drawNativeDonutWithLabels(canvas, labels, data, colors, centerText = null, centerSub = null) {
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const w = canvas.parentElement ? (canvas.parentElement.clientWidth || 360) : 360;
    const h = 260;
    canvas.width = w;
    canvas.height = h;
    ctx.clearRect(0, 0, w, h);

    const total = data.reduce((a, b) => a + b, 0) || 1;
    const cx = w / 2;
    const cy = 95;
    const radius = 68;
    const innerRadius = 44;

    let startAngle = -Math.PI / 2;
    for (let i = 0; i < data.length; i++) {
      const sliceAngle = (data[i] / total) * 2 * Math.PI;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, startAngle, startAngle + sliceAngle);
      ctx.arc(cx, cy, innerRadius, startAngle + sliceAngle, startAngle, true);
      ctx.closePath();
      ctx.fillStyle = colors[i % colors.length];
      ctx.fill();
      ctx.strokeStyle = "#FFFFFF";
      ctx.lineWidth = 2;
      ctx.stroke();
      startAngle += sliceAngle;
    }

    if (centerText) {
      ctx.fillStyle = PALETTE.navyDark;
      ctx.font = "bold 18px -apple-system, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(centerText, cx, cy - 6);

      if (centerSub) {
        ctx.fillStyle = PALETTE.slate;
        ctx.font = "600 10px -apple-system, sans-serif";
        ctx.fillText(centerSub, cx, cy + 11);
      }
    }

    // Legend placed cleanly below the donut
    let legendY = 185;
    ctx.font = "600 11px -apple-system, sans-serif";
    for (let i = 0; i < labels.length; i++) {
      ctx.fillStyle = colors[i % colors.length];
      ctx.fillRect(cx - 100, legendY - 9, 10, 10);
      ctx.fillStyle = PALETTE.navyDark;
      ctx.textAlign = "left";
      ctx.fillText(labels[i], cx - 84, legendY);
      legendY += 22;
    }
  },

  drawNativeBar(canvas, labels, data, color, unit = "") {
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const w = canvas.parentElement.clientWidth || 400;
    const h = 250;
    canvas.width = w;
    canvas.height = h;
    ctx.clearRect(0, 0, w, h);

    const maxVal = Math.max(...data, 1);
    const bottom = h - 35;
    const chartHeight = bottom - 25;
    const slotW = (w - 40) / (labels.length || 1);

    labels.forEach((lbl, i) => {
      const x = 25 + i * slotW;
      const barH = (data[i] / maxVal) * chartHeight;
      const barW = Math.min(28, slotW * 0.6);

      ctx.fillStyle = color;
      ctx.fillRect(x + (slotW - barW) / 2, bottom - barH, barW, barH);

      ctx.fillStyle = PALETTE.navyDark;
      ctx.font = "600 10px -apple-system, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(`${data[i]}${unit}`, x + slotW / 2, bottom - barH - 4);

      ctx.fillStyle = PALETTE.slate;
      ctx.font = "10px -apple-system, sans-serif";
      const shortLbl = lbl.length > 7 ? lbl.substring(0, 6) + ".." : lbl;
      ctx.fillText(shortLbl, x + slotW / 2, bottom + 16);
    });
  },

  drawNativeLine(canvas, labels, data, color, unit = "") {
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const w = canvas.parentElement.clientWidth || 400;
    const h = 250;
    canvas.width = w;
    canvas.height = h;
    ctx.clearRect(0, 0, w, h);

    const maxVal = Math.max(...data, 1);
    const bottom = h - 35;
    const chartHeight = bottom - 30;
    const slotW = (w - 50) / (labels.length - 1 || 1);

    ctx.strokeStyle = color;
    ctx.lineWidth = 2.2;
    ctx.beginPath();

    data.forEach((val, i) => {
      const x = 30 + i * slotW;
      const y = bottom - (val / maxVal) * chartHeight;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Draw points and labels
    data.forEach((val, i) => {
      const x = 30 + i * slotW;
      const y = bottom - (val / maxVal) * chartHeight;
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, 3, 0, 2 * Math.PI);
      ctx.fill();

      ctx.fillStyle = PALETTE.slate;
      ctx.font = "9px -apple-system, sans-serif";
      ctx.textAlign = "center";
      const shortLbl = labels[i].length > 7 ? labels[i].slice(-5) : labels[i];
      ctx.fillText(shortLbl, x, bottom + 16);
    });
  }
};

if (typeof window !== "undefined") {
  window.Charts = Charts;
}
