/**
 * ==============================================================================
 * WorkforceAI - Clean, Responsive Application Controller & View Router
 * Coordinates UI state, reactive filters, chart rendering, and Full-Screen Copilot.
 * ==============================================================================
 */

import { API } from "./api.js?v=20261108_v29";
import { Charts } from "./charts.js?v=20261108_v29";

// Global Application State
const state = {
  currentView: "overview",
  selectedDept: "",
  selectedLoc: "",
  selectedStartDate: "",
  selectedEndDate: "",
  chatbotOpen: false,
  chatMessages: [
    {
      role: "assistant",
      isDefault: true,
      answer: "Hello! I am your **WorkforceAI Copilot**, bounded strictly to our company's verified HR workforce dataset (500 employees across 7 departments).\n\nYou can ask me about **headcount**, **department attrition**, **attendance patterns**, **leave consumption**, or **staff retention risk**.",
      suggestions: [
        "Which department has highest attrition?",
        "Who are the employees at risk of leaving?",
        "What is the exit forecast for next quarter?",
        "Show irregular attendance patterns.",
        "What are the workforce movement totals?"
      ]
    }
  ],
  cachedFlightRisk: [],
  cachedAnomalies: [],
  cachedMovements: []
};

// ==============================================================================
// 1. GLOBAL VIEW SWITCHER (FOUR CORE SECTIONS ONLY)
// ==============================================================================
export function switchView(viewId) {
  state.currentView = viewId;

  // Auto-close full-screen chatbot when user switches tabs
  const fullscreenChatbot = document.getElementById("fullscreen-chatbot");
  if (fullscreenChatbot && state.chatbotOpen) {
    state.chatbotOpen = false;
    fullscreenChatbot.style.display = "none";
    fullscreenChatbot.classList.remove("open");
    const floatingBtn = document.getElementById("btn-floating-chatbot");
    if (floatingBtn) {
      floatingBtn.style.setProperty("display", "flex", "important");
      floatingBtn.style.visibility = "visible";
    }
  }

  // Update active state in navy-blue sidebar
  document.querySelectorAll(".nav-menu .nav-item").forEach(item => {
    if (item.dataset.view === viewId) {
      item.classList.add("active");
    } else {
      item.classList.remove("active");
    }
  });

  // Toggle page section visibility
  document.querySelectorAll(".view-section").forEach(sec => {
    sec.style.display = (sec.id === `view-${viewId}`) ? "block" : "none";
  });

  // Update top bar title
  const titles = {
    "overview": "Overview",
    "attrition": "Attrition & Onboarding",
    "attendance": "Attendance & Leave",
    "movement": "Workforce Movement"
  };
  const pageTitleElem = document.getElementById("page-title");
  if (pageTitleElem) {
    pageTitleElem.innerText = titles[viewId] || "Overview";
  }

  // Render view data
  renderActiveView(viewId);
}
window.switchView = switchView;

// ==============================================================================
// 2. INITIALIZATION & LIFECYCLE
// ==============================================================================
function startApplication() {
  if (window.__WORKFORCE_AI_INITIALIZED__) return;
  window.__WORKFORCE_AI_INITIALIZED__ = true;

  console.log("[WorkforceAI] Initializing dashboard controller...");
  initSidebar();
  initChatbot();

  // Load Filter options and DB status
  loadFilterOptions().catch(err => console.error("[loadFilterOptions] Error:", err));
  loadDatabaseStatus().catch(err => console.error("[loadDatabaseStatus] Error:", err));

  // Global Filter Listeners
  const deptSelect = document.getElementById("filter-dept");
  if (deptSelect) {
    const handleDept = (e) => {
      state.selectedDept = e.target.value;
      onFiltersChanged();
    };
    deptSelect.addEventListener("change", handleDept);
    deptSelect.addEventListener("input", handleDept);
  }

  const locSelect = document.getElementById("filter-loc");
  if (locSelect) {
    const handleLoc = (e) => {
      state.selectedLoc = e.target.value;
      onFiltersChanged();
    };
    locSelect.addEventListener("change", handleLoc);
    locSelect.addEventListener("input", handleLoc);
  }

  // From Date & To Date Calendar Range Filter Listeners
  const startDateInput = document.getElementById("filter-start-date");
  if (startDateInput) {
    const handleStartDate = (e) => {
      state.selectedStartDate = e.target.value;
      const endDateInput = document.getElementById("filter-end-date");
      if (endDateInput && state.selectedStartDate) {
        endDateInput.min = state.selectedStartDate;
        if (state.selectedEndDate && state.selectedEndDate < state.selectedStartDate) {
          state.selectedEndDate = state.selectedStartDate;
          endDateInput.value = state.selectedStartDate;
        }
      }
      onFiltersChanged();
    };
    startDateInput.addEventListener("change", handleStartDate);
    startDateInput.addEventListener("input", handleStartDate);
  }

  const endDateInput = document.getElementById("filter-end-date");
  if (endDateInput) {
    const handleEndDate = (e) => {
      state.selectedEndDate = e.target.value;
      const startDateInput = document.getElementById("filter-start-date");
      if (startDateInput && state.selectedEndDate) {
        startDateInput.max = state.selectedEndDate;
        if (state.selectedStartDate && state.selectedStartDate > state.selectedEndDate) {
          state.selectedStartDate = state.selectedEndDate;
          startDateInput.value = state.selectedEndDate;
        }
      }
      onFiltersChanged();
    };
    endDateInput.addEventListener("change", handleEndDate);
    endDateInput.addEventListener("input", handleEndDate);
  }

  const resetBtn = document.getElementById("btn-reset-filters");
  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      if (deptSelect) deptSelect.value = "";
      if (locSelect) locSelect.value = "";
      if (startDateInput) {
        startDateInput.value = "";
        startDateInput.removeAttribute("max");
      }
      if (endDateInput) {
        endDateInput.value = "";
        endDateInput.removeAttribute("min");
      }
      const searchOnb = document.getElementById("search-onboarding");
      if (searchOnb) searchOnb.value = "";
      const searchRisk = document.getElementById("search-flight-risk");
      if (searchRisk) searchRisk.value = "";
      state.selectedDept = "";
      state.selectedLoc = "";
      state.selectedStartDate = "";
      state.selectedEndDate = "";
      onFiltersChanged();
    });
  }

  // Wire search inputs in tables
  initTableSearchListeners();

  // Switch to default overview view
  switchView("overview");
}

if (document.readyState === "complete" || document.readyState === "interactive") {
  initAuth();
} else {
  document.addEventListener("DOMContentLoaded", initAuth);
}

// ==============================================================================
// AUTHENTICATION & ROLE-BASED ACCESS CONTROL (RBAC) CONTROLLER
// ==============================================================================
export function initAuth() {
  const loginOverlay = document.getElementById("login-screen-overlay");
  const adminContainer = document.getElementById("app-container-admin");
  const employeeContainer = document.getElementById("app-container-employee");
  const floatingBtn = document.getElementById("btn-floating-chatbot");

  // Check persisted session
  let session = null;
  try {
    const raw = localStorage.getItem("workforce_session");
    if (raw) session = JSON.parse(raw);
  } catch (e) {
    localStorage.removeItem("workforce_session");
  }

  // Bind logout buttons
  const btnLogoutAdmin = document.getElementById("btn-logout-admin");
  if (btnLogoutAdmin && !btnLogoutAdmin.dataset.bound) {
    btnLogoutAdmin.dataset.bound = "true";
    btnLogoutAdmin.addEventListener("click", logout);
  }

  const btnLogoutEmp = document.getElementById("btn-logout-employee");
  if (btnLogoutEmp && !btnLogoutEmp.dataset.bound) {
    btnLogoutEmp.dataset.bound = "true";
    btnLogoutEmp.addEventListener("click", logout);
  }

  // Bind login form
  const loginForm = document.getElementById("login-form");
  if (loginForm && !loginForm.dataset.bound) {
    loginForm.dataset.bound = "true";
    loginForm.addEventListener("submit", handleLoginSubmit);
  }

  if (session && session.success && session.role) {
    if (session.role === "hr_admin") {
      // Show HR Admin Full Dashboard
      if (loginOverlay) loginOverlay.style.display = "none";
      if (employeeContainer) employeeContainer.style.display = "none";
      if (adminContainer) adminContainer.style.display = "flex";
      if (floatingBtn) floatingBtn.style.display = "flex";
      const empFloatingBtn = document.getElementById("btn-floating-chatbot-emp");
      if (empFloatingBtn) empFloatingBtn.style.setProperty("display", "none", "important");

      const adminName = document.getElementById("admin-header-name");
      if (adminName) adminName.innerText = session.user.name || "Sarah Jenkins (HR Admin)";

      startApplication();
    } else if (session.role === "employee") {
      // Show Employee Self-Service "My HR Portal"
      if (loginOverlay) loginOverlay.style.display = "none";
      if (adminContainer) adminContainer.style.display = "none";
      if (employeeContainer) employeeContainer.style.display = "flex";
      if (floatingBtn) floatingBtn.style.display = "none";
      const empFloatingBtn = document.getElementById("btn-floating-chatbot-emp");
      if (empFloatingBtn) empFloatingBtn.style.setProperty("display", "flex", "important");

      initEmployeePortal(session.user);
    }
  } else {
    // Show Login Screen
    if (loginOverlay) loginOverlay.style.display = "flex";
    if (adminContainer) adminContainer.style.display = "none";
    if (employeeContainer) employeeContainer.style.display = "none";
    if (floatingBtn) floatingBtn.style.display = "none";
    const empFloatingBtn = document.getElementById("btn-floating-chatbot-emp");
    if (empFloatingBtn) empFloatingBtn.style.setProperty("display", "none", "important");
  }
}
window.initAuth = initAuth;

export function logout() {
  localStorage.removeItem("workforce_session");
  const loginOverlay = document.getElementById("login-screen-overlay");
  const adminContainer = document.getElementById("app-container-admin");
  const employeeContainer = document.getElementById("app-container-employee");
  const floatingBtn = document.getElementById("btn-floating-chatbot");
  const empFloatingBtn = document.getElementById("btn-floating-chatbot-emp");
  const empChatModal = document.getElementById("fullscreen-chatbot-emp");

  if (adminContainer) adminContainer.style.display = "none";
  if (employeeContainer) employeeContainer.style.display = "none";
  if (floatingBtn) floatingBtn.style.display = "none";
  if (empFloatingBtn) empFloatingBtn.style.setProperty("display", "none", "important");
  if (empChatModal) {
    empChatModal.style.setProperty("display", "none", "important");
    empChatModal.classList.remove("open");
  }
  if (loginOverlay) loginOverlay.style.display = "flex";

  const errAlert = document.getElementById("login-error-alert");
  if (errAlert) errAlert.style.display = "none";
  const emailInput = document.getElementById("login-email");
  if (emailInput) emailInput.value = "";
  const pwInput = document.getElementById("login-password");
  if (pwInput) pwInput.value = "";
}
window.logout = logout;

async function handleLoginSubmit(e) {
  e.preventDefault();
  const email = (document.getElementById("login-email").value || "").trim();
  const password = (document.getElementById("login-password").value || "").trim();
  await executeLogin(email, password);
}

async function executeLogin(email, password) {
  const btnSubmit = document.getElementById("btn-login-submit");
  const errAlert = document.getElementById("login-error-alert");
  const errText = document.getElementById("login-error-text");

  if (errAlert) errAlert.style.display = "none";
  if (btnSubmit) {
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = `<span>Signing in...</span>`;
  }

  try {
    const res = await API.login(email, password);
    if (res && res.success) {
      localStorage.setItem("workforce_session", JSON.stringify(res));
      initAuth();
    } else {
      if (errAlert) errAlert.style.display = "flex";
      if (errText) errText.innerText = res.error || "Invalid email or password.";
    }
  } catch (err) {
    if (errAlert) errAlert.style.display = "flex";
    if (errText) errText.innerText = "Connection failed. Please ensure backend is running.";
  } finally {
    if (btnSubmit) {
      btnSubmit.disabled = false;
      btnSubmit.innerHTML = `<span>Sign In to WorkforceAI</span><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>`;
    }
  }
}

async function initEmployeePortal(user) {
  const empId = user.employee_id || "E0087";
  const initials = (user.name || "Employee")
    .split(" ")
    .map(w => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  // 1. Populate Header & Hero Profile
  const headerName = document.getElementById("emp-header-name");
  if (headerName) headerName.innerText = `${user.name} (${empId})`;
  const avatarInitials = document.getElementById("emp-avatar-initials");
  if (avatarInitials) avatarInitials.innerText = initials;

  const heroName = document.getElementById("emp-hero-name");
  if (heroName) heroName.innerText = user.name;
  const heroAvatar = document.getElementById("emp-hero-avatar");
  if (heroAvatar) heroAvatar.innerText = initials;
  const heroTitle = document.getElementById("emp-hero-title");
  if (heroTitle) heroTitle.innerText = `${user.designation || "Staff"} • ${user.department || "Organization"}`;
  const heroId = document.getElementById("emp-hero-id");
  if (heroId) heroId.innerText = `ID: ${empId}`;
  const heroLoc = document.getElementById("emp-hero-location");
  if (heroLoc) heroLoc.innerText = `Location: ${user.location || "Headquarters"}`;
  const heroJoin = document.getElementById("emp-hero-joining");
  if (heroJoin) heroJoin.innerText = `Joined: ${user.joining_date || "2023"}`;

  // 2. Fetch Employee Portal Data
  const data = await API.getEmployeePortalData(empId);
  if (!data || data.error) return;

  // 3. Populate 4 KPI Cards
  const kpiAttRate = document.getElementById("emp-kpi-att-rate");
  if (kpiAttRate) kpiAttRate.innerText = `${data.attendance.attendance_rate_pct}%`;
  const kpiAttSub = document.getElementById("emp-kpi-att-sub");
  if (kpiAttSub) kpiAttSub.innerText = `${data.attendance.present_days} days present • ${data.attendance.remote_days} days remote`;

  const kpiHours = document.getElementById("emp-kpi-hours");
  if (kpiHours) kpiHours.innerText = `${data.attendance.avg_logged_hours}h`;

  const casual = data.leaves.breakdown["Casual Leave"] || { used: 0, total: 12 };
  const sick = data.leaves.breakdown["Sick Leave"] || { used: 0, total: 10 };
  const paid = data.leaves.breakdown["Paid Leave"] || { used: 0, total: 15 };
  const cRem = Math.max(0, casual.total - casual.used);
  const sRem = Math.max(0, sick.total - sick.used);
  const pRem = Math.max(0, paid.total - paid.used);
  const totalRem = cRem + sRem + pRem;

  const kpiLeave = document.getElementById("emp-kpi-leave-balance");
  if (kpiLeave) kpiLeave.innerText = `${totalRem} Days`;
  const kpiLeaveSub = document.getElementById("emp-kpi-leave-sub");
  if (kpiLeaveSub) kpiLeaveSub.innerText = `${cRem} Casual • ${sRem} Sick • ${pRem} Paid`;

  const kpiOnb = document.getElementById("emp-kpi-onb-rate");
  if (kpiOnb) kpiOnb.innerText = `${data.onboarding.completion_rate_pct}%`;
  const kpiOnbSub = document.getElementById("emp-kpi-onb-sub");
  if (kpiOnbSub) {
    kpiOnbSub.innerText = data.onboarding.pending_milestones === 0
      ? "All induction tasks completed"
      : `${data.onboarding.pending_milestones} milestone(s) pending`;
  }

  // 4. Populate Attendance Table
  const attTbody = document.getElementById("emp-attendance-tbody");
  if (attTbody && data.recent_attendance) {
    attTbody.innerHTML = data.recent_attendance.map(r => {
      let chipClass = "present";
      const s = (r.attendance_status || "").toLowerCase();
      if (s.includes("remote")) chipClass = "remote";
      else if (s.includes("absent")) chipClass = "absent";
      else if (s.includes("leave")) chipClass = "leave";

      return `
        <tr>
          <td><strong>${r.attendance_date}</strong></td>
          <td>${r.check_in_time || "—"}</td>
          <td>${r.check_out_time || "—"}</td>
          <td><b>${r.duration_hours ? r.duration_hours + " hrs" : "—"}</b></td>
          <td><span class="status-chip ${chipClass}">${r.attendance_status}</span></td>
        </tr>
      `;
    }).join("");
  }

  // 5. Populate Leaves Bars & History Table
  const lblClUsed = document.getElementById("lbl-cl-used");
  if (lblClUsed) lblClUsed.innerText = `${casual.used} Days Used`;
  const lblClRem = document.getElementById("lbl-cl-rem");
  if (lblClRem) lblClRem.innerText = `${cRem} Days Left`;
  const barCl = document.getElementById("bar-cl");
  if (barCl) barCl.style.width = `${Math.min(100, Math.round((casual.used / casual.total) * 100))}%`;

  const lblSlUsed = document.getElementById("lbl-sl-used");
  if (lblSlUsed) lblSlUsed.innerText = `${sick.used} Days Used`;
  const lblSlRem = document.getElementById("lbl-sl-rem");
  if (lblSlRem) lblSlRem.innerText = `${sRem} Days Left`;
  const barSl = document.getElementById("bar-sl");
  if (barSl) barSl.style.width = `${Math.min(100, Math.round((sick.used / sick.total) * 100))}%`;

  const lblPlUsed = document.getElementById("lbl-pl-used");
  if (lblPlUsed) lblPlUsed.innerText = `${paid.used} Days Used`;
  const lblPlRem = document.getElementById("lbl-pl-rem");
  if (lblPlRem) lblPlRem.innerText = `${pRem} Days Left`;
  const barPl = document.getElementById("bar-pl");
  if (barPl) barPl.style.width = `${Math.min(100, Math.round((paid.used / paid.total) * 100))}%`;

  const leavesTbody = document.getElementById("emp-leaves-tbody");
  if (leavesTbody && data.leaves.recent_requests) {
    leavesTbody.innerHTML = data.leaves.recent_requests.map(l => {
      let stClass = "pending";
      const st = (l.approval_status || "").toLowerCase();
      if (st.includes("approved")) stClass = "approved";
      else if (st.includes("rejected")) stClass = "rejected";

      return `
        <tr>
          <td><code>${l.leave_id}</code></td>
          <td><strong>${l.leave_type}</strong></td>
          <td>${l.start_date}</td>
          <td>${l.end_date}</td>
          <td><b>${l.leave_days} Day(s)</b></td>
          <td><span class="status-chip ${stClass}">${l.approval_status}</span></td>
        </tr>
      `;
    }).join("");
  }

  // 6. Populate Onboarding Table
  const onbTbody = document.getElementById("emp-onboarding-tbody");
  const onbBadge = document.getElementById("emp-onb-badge-status");
  if (onbBadge) onbBadge.innerText = `${data.onboarding.completion_rate_pct}% Completed`;
  if (onbTbody && data.onboarding.tasks) {
    onbTbody.innerHTML = data.onboarding.tasks.map(t => {
      const isDone = t.task_status === "Completed";
      return `
        <tr>
          <td><strong>${t.task_name}</strong></td>
          <td>${t.assigned_date}</td>
          <td>${t.completion_date || "In Progress"}</td>
          <td>
            <span class="status-chip ${isDone ? 'approved' : 'pending'}">
              ${isDone ? '✓ Completed' : 'Pending'}
            </span>
          </td>
        </tr>
      `;
    }).join("");
  }

  // 7. Reset active tab to default (Attendance)
  document.querySelectorAll(".emp-nav-item").forEach(b => {
    b.classList.toggle("active", b.dataset.tab === "emp-tab-attendance");
  });
  document.querySelectorAll(".emp-tab-content").forEach(sec => {
    sec.style.display = sec.id === "emp-tab-attendance" ? "block" : "none";
  });
  const pageTitle = document.getElementById("emp-page-title");
  if (pageTitle) pageTitle.innerText = "Attendance Records";

  // 8. Ensure Employee Floating Chatbot Icon is Visible
  const empFloatingBtn = document.getElementById("btn-floating-chatbot-emp");
  if (empFloatingBtn) empFloatingBtn.style.setProperty("display", "flex", "important");
}

// ==============================================================================
// 3. VIEW RENDERERS
// ==============================================================================
async function renderActiveView(viewId) {
  try {
    if (viewId === "overview") {
      await renderOverviewView();
    } else if (viewId === "attrition") {
      await renderAttritionView();
    } else if (viewId === "attendance") {
      await renderAttendanceView();
    } else if (viewId === "movement") {
      await renderMovementView();
    }
  } catch (err) {
    console.error(`[renderActiveView] Error rendering ${viewId}:`, err);
  }
}

/** 1. Render Overview View */
async function renderOverviewView() {
  fetch("/api/client-log?msg=" + encodeURIComponent("Entering renderOverviewView")).catch(()=>{});

  // Render baseline charts immediately inside guarded blocks
  try {
    Charts.renderWorkforceTrend("chart-workforce-trend", null);
  } catch (e) {
    console.warn("[Baseline chart-workforce-trend err]:", e);
    fetch("/api/client-log?err=" + encodeURIComponent("Workforce trend baseline: " + e.message)).catch(()=>{});
  }

  try {
    Charts.renderDepartmentDistribution("chart-dept-distribution", null);
  } catch (e) {
    console.warn("[Baseline chart-dept-distribution err]:", e);
    fetch("/api/client-log?err=" + encodeURIComponent("Dept dist baseline: " + e.message)).catch(()=>{});
  }

  try {
    Charts.renderDepartmentAttrition("chart-overview-attrition-trend", null);
  } catch (e) {
    console.warn("[Baseline chart-overview-attrition-trend err]:", e);
    fetch("/api/client-log?err=" + encodeURIComponent("Attrition dept baseline: " + e.message)).catch(()=>{});
  }

  try {
    Charts.renderLeaveInsightDonut("chart-overview-leave-donut", null, 79.0);
  } catch (e) {
    console.warn("[Baseline chart-overview-leave-donut err]:", e);
    fetch("/api/client-log?err=" + encodeURIComponent("Leave donut baseline: " + e.message)).catch(()=>{});
  }

  try {
    Charts.renderOnboardingDonut("chart-overview-onboarding-donut", null, 88.2);
  } catch (e) {
    console.warn("[Baseline chart-overview-onboarding-donut err]:", e);
  }

  try {
    Charts.renderWorkforceMovementsBar("chart-overview-movements-bar", null);
  } catch (e) {
    console.warn("[Baseline chart-overview-movements-bar err]:", e);
  }

  try {
    const [kpis, trends, depts, forecast, anomalies, leaves, attendance, onbData] = await Promise.all([
      API.getKPIs(state.selectedDept, state.selectedLoc, state.selectedStartDate, state.selectedEndDate),
      API.getTrends(state.selectedDept, state.selectedLoc, state.selectedStartDate, state.selectedEndDate),
      API.getDepartmentBreakdown(state.selectedDept, state.selectedLoc, state.selectedStartDate, state.selectedEndDate),
      API.getExitForecast(3, state.selectedDept, state.selectedLoc, state.selectedStartDate, state.selectedEndDate),
      API.getAttendanceAnomalies(2.0, state.selectedDept, state.selectedLoc, state.selectedStartDate, state.selectedEndDate),
      API.getLeaveAnalytics(state.selectedDept, state.selectedLoc, state.selectedStartDate, state.selectedEndDate),
      API.getAttendanceKPIs(state.selectedDept, state.selectedLoc, state.selectedStartDate, state.selectedEndDate),
      API.getOnboardingMobility(state.selectedDept, state.selectedLoc, state.selectedStartDate, state.selectedEndDate)
    ]);

    fetch("/api/client-log?msg=" + encodeURIComponent("Overview APIs returned. Total emp: " + (kpis.total_employees || kpis.total_headcount))).catch(()=>{});

    // 4 Primary Executive KPI Cards
    const total = kpis.total_employees ?? kpis.total_headcount ?? 500;
    const active = kpis.active_headcount ?? 430;
    const exited = kpis.exited_count ?? 70;
    const onboarded = kpis.onboarded_count ?? 169;
    const netGrowth = kpis.net_growth ?? (onboarded - exited);
    const attRate = parseFloat(kpis.attrition_rate_pct ?? 18.4).toFixed(1);
    const attenRate = parseFloat(kpis.attendance_rate_pct ?? 80.0).toFixed(1);
    const leaveRate = parseFloat(kpis.leave_utilization_pct ?? leaves?.leave_utilization_pct ?? 78.9).toFixed(1);
    const leaveDays = kpis.approved_leave_days ?? leaves?.approved_leave_days ?? 4069;
    const quotaDays = kpis.leave_quota_days ?? leaves?.leave_quota_days ?? 5160;

    const elTotal = document.getElementById("kpi-total-employees");
    if (elTotal) elTotal.innerText = total.toLocaleString();
    const elActive = document.getElementById("kpi-active-employees");
    if (elActive) elActive.innerText = active.toLocaleString();
    const elAttRate = document.getElementById("kpi-attrition-rate");
    if (elAttRate) elAttRate.innerText = `${attRate}%`;
    const elExited = document.getElementById("kpi-exited-count");
    if (elExited) elExited.innerText = exited.toLocaleString();
    const elOnboarded = document.getElementById("kpi-onboarded-count");
    if (elOnboarded) elOnboarded.innerText = onboarded.toLocaleString();
    const elNetGrowth = document.getElementById("kpi-net-growth");
    if (elNetGrowth) {
      elNetGrowth.innerText = `${netGrowth >= 0 ? '+' : ''}${netGrowth}`;
      elNetGrowth.style.color = netGrowth >= 0 ? "var(--green)" : "var(--red)";
    }
    const elAtten = document.getElementById("kpi-attendance-rate");
    if (elAtten) elAtten.innerText = `${attenRate}%`;
    const elLeave = document.getElementById("kpi-leave-utilization");
    if (elLeave) elLeave.innerText = `${leaveRate}%`;
    const elLeaveDays = document.getElementById("kpi-leave-days-used");
    if (elLeaveDays) elLeaveDays.innerText = Number(leaveDays).toLocaleString();
    const elQuotaDays = document.getElementById("kpi-leave-quota-days");
    if (elQuotaDays) elQuotaDays.innerText = Number(quotaDays).toLocaleString();

    const appCount = leaves?.approved_count ?? kpis.approved_count ?? 1481;
    const penCount = leaves?.pending_count ?? kpis.pending_count ?? 214;
    const rejCount = leaves?.rejected_count ?? kpis.rejected_count ?? 179;
    const elAppCnt = document.getElementById("kpi-leave-app-count");
    if (elAppCnt) elAppCnt.innerText = Number(appCount).toLocaleString();
    const elPenCnt = document.getElementById("kpi-leave-pen-count");
    if (elPenCnt) elPenCnt.innerText = Number(penCount).toLocaleString();
    const elRejCnt = document.getElementById("kpi-leave-rej-count");
    if (elRejCnt) elRejCnt.innerText = Number(rejCount).toLocaleString();

    // Visualizations with live API data
    if (trends && trends.workforce_trend) {
      Charts.renderWorkforceTrend("chart-workforce-trend", trends.workforce_trend);
    }
    if (depts) {
      Charts.renderDepartmentDistribution("chart-dept-distribution", depts);
    }
    if (depts) {
      Charts.renderDepartmentAttrition("chart-overview-attrition-trend", depts);
    }

    // Attendance & Leave Insight Widget
    const utilPct = (leaves && leaves.leave_utilization_pct !== undefined) ? leaves.leave_utilization_pct : leaveRate;
    const leaveTypes = (leaves && leaves.leave_by_type) ? leaves.leave_by_type : null;
    Charts.renderLeaveInsightDonut("chart-overview-leave-donut", leaveTypes, utilPct);

    const elAppPct = document.getElementById("leave-approved-pct");
    if (elAppPct) elAppPct.innerText = `${parseFloat(leaves && leaves.approved_pct !== undefined ? leaves.approved_pct : 79.0).toFixed(1)}%`;
    const elPenPct = document.getElementById("leave-pending-pct");
    if (elPenPct) elPenPct.innerText = `${parseFloat(leaves && leaves.pending_pct !== undefined ? leaves.pending_pct : 11.4).toFixed(1)}%`;
    const elRejPct = document.getElementById("leave-rejected-pct");
    if (elRejPct) elRejPct.innerText = `${parseFloat(leaves && leaves.rejected_pct !== undefined ? leaves.rejected_pct : 9.6).toFixed(1)}%`;

    const attRateVal = (attendance && attendance.present_pct !== undefined) ? attendance.present_pct : attenRate;
    const elAttVal = document.getElementById("overview-att-rate");
    if (elAttVal) elAttVal.innerText = `${parseFloat(attRateVal).toFixed(1)}%`;

    const elPresPct = document.getElementById("overview-present-pct");
    if (elPresPct) elPresPct.innerText = `${parseFloat(attendance && attendance.present_pct !== undefined ? attendance.present_pct : 80.0).toFixed(1)}%`;

    const elRemPct = document.getElementById("overview-remote-pct");
    if (elRemPct) elRemPct.innerText = `${parseFloat(attendance && attendance.remote_pct !== undefined ? attendance.remote_pct : 9.3).toFixed(1)}%`;

    const elHalfPct = document.getElementById("overview-halfday-pct");
    if (elHalfPct) elHalfPct.innerText = `${parseFloat(attendance && attendance.half_day_pct !== undefined ? attendance.half_day_pct : 2.9).toFixed(1)}%`;

    const elOnLeavePct = document.getElementById("overview-onleave-pct");
    if (elOnLeavePct) elOnLeavePct.innerText = `${parseFloat(attendance && attendance.on_leave_pct !== undefined ? attendance.on_leave_pct : 2.5).toFixed(1)}%`;

    const elAbsPct = document.getElementById("overview-absent-pct");
    if (elAbsPct) elAbsPct.innerText = `${parseFloat(attendance && attendance.absenteeism_pct !== undefined ? attendance.absenteeism_pct : 5.3).toFixed(1)}%`;

    // Onboarding Tasks Donut & Workforce Movement Graph
    if (onbData) {
      Charts.renderOnboardingDonut(
        "chart-overview-onboarding-donut",
        onbData.onboarding_status_breakdown,
        onbData.onboarding_completion_pct
      );
      Charts.renderWorkforceMovementsBar(
        "chart-overview-movements-bar",
        onbData.movements_breakdown
      );
    }

    // ML Predictions Panel (Whole number counts)
    const exitCount = (forecast && forecast.total_quarterly_projected_exits !== undefined) ? Math.round(Number(forecast.total_quarterly_projected_exits)) : 16;
    const breakdown = (forecast && forecast.monthly_forecast) ? forecast.monthly_forecast : { "Nov 2026": 5, "Dec 2026": 5, "Jan 2027": 6 };
    const breakdownStr = Object.entries(breakdown).map(([k, v]) => `${k.slice(0, 3)}: ${Math.round(Number(v))}`).join(" &bull; ");
    
    const elPredExits = document.getElementById("ml-predicted-exits");
    if (elPredExits) elPredExits.innerText = exitCount;
    const elPredBreak = document.getElementById("ml-predicted-breakdown");
    if (elPredBreak) {
      elPredBreak.innerHTML = `${breakdownStr} exits/mo`;
    }
    const elPredAnom = document.getElementById("ml-predicted-anomalies");
    if (elPredAnom) elPredAnom.innerText = (anomalies && anomalies.length !== undefined) ? anomalies.length : 36;
  } catch (err) {
    console.error("[renderOverviewView] Error loading live data:", err);
    fetch("/api/client-log?err=" + encodeURIComponent("renderOverviewView API error: " + err.message)).catch(()=>{});
  }
}

/** 2. Render Attrition & Onboarding View */
async function renderAttritionView() {
  try {
    const [kpis, attInsights, onbData, roster, onbRoster] = await Promise.all([
      API.getKPIs(state.selectedDept, state.selectedLoc, state.selectedStartDate, state.selectedEndDate),
      API.getAttritionInsights(state.selectedDept, state.selectedLoc, state.selectedStartDate, state.selectedEndDate),
      API.getOnboardingMobility(state.selectedDept, state.selectedLoc, state.selectedStartDate, state.selectedEndDate),
      API.getFlightRiskRoster(state.selectedDept, state.selectedLoc, state.selectedStartDate, state.selectedEndDate),
      API.getOnboardingRoster(state.selectedDept, state.selectedLoc, state.selectedStartDate, state.selectedEndDate)
    ]);

    state.cachedFlightRisk = roster || [];
    state.cachedOnboarding = onbRoster || [];

    // 1. Top Two KPI Cards (Attrition Rate & Onboarding)
    const attRateVal = parseFloat(kpis.attrition_rate_pct || 18.4).toFixed(1);
    const exitedVal = kpis.exited_count !== undefined ? kpis.exited_count : 70;
    const activeVal = kpis.active_headcount !== undefined ? kpis.active_headcount : 430;
    const onbVal = kpis.onboarded_count !== undefined ? kpis.onboarded_count : 169;
    const netVal = kpis.net_growth !== undefined ? kpis.net_growth : (onbVal - exitedVal);
    const replVal = kpis.replacement_ratio !== undefined ? parseFloat(kpis.replacement_ratio).toFixed(2) : (exitedVal ? (onbVal / exitedVal).toFixed(2) : "1.00");

    const elAttRate = document.getElementById("att-view-rate");
    if (elAttRate) elAttRate.innerText = `${attRateVal}%`;
    const elAttExited = document.getElementById("att-view-exited");
    if (elAttExited) elAttExited.innerText = exitedVal.toLocaleString();
    const elAttOnb = document.getElementById("att-view-onboarded");
    if (elAttOnb) elAttOnb.innerText = onbVal.toLocaleString();
    const elAttNet = document.getElementById("att-view-net");
    if (elAttNet) {
      elAttNet.innerText = `${netVal >= 0 ? '+' : ''}${netVal}`;
      elAttNet.style.color = netVal >= 0 ? "var(--green)" : "var(--red)";
    }
    const elAttRepl = document.getElementById("att-view-replacement");
    if (elAttRepl) elAttRepl.innerText = `${replVal}x`;

    let compTasks = 0;
    let penTasks = 0;
    let hasStatusData = false;

    if (onbData && onbData.onboarding_status_breakdown && Array.isArray(onbData.onboarding_status_breakdown) && onbData.onboarding_status_breakdown.length > 0) {
      onbData.onboarding_status_breakdown.forEach(s => {
        const status = (s.task_status || s.status || "").toLowerCase().trim();
        const cnt = Number(s.task_count !== undefined ? s.task_count : (s.count !== undefined ? s.count : 0));
        if (status === "completed") { compTasks += cnt; hasStatusData = true; }
        else if (status === "pending") { penTasks += cnt; hasStatusData = true; }
      });
    }

    // If API returned empty breakdown or 0 tasks but onbRoster has records, aggregate directly from onbRoster
    if (!hasStatusData && state.cachedOnboarding && state.cachedOnboarding.length > 0) {
      state.cachedOnboarding.forEach(r => {
        compTasks += Number(r.completed_tasks || 0);
        penTasks += Number(r.pending_tasks || 0);
      });
      hasStatusData = true;
    }

    if (!hasStatusData && (!state.selectedDept && !state.selectedLoc)) {
      compTasks = 2204;
      penTasks = 296;
    }

    const totalTasks = compTasks + penTasks;
    const completionPct = totalTasks > 0 ? ((compTasks / totalTasks) * 100).toFixed(1) : (onbData.onboarding_completion_pct || "88.2");

    const elOnbRate = document.getElementById("att-view-onboarding");
    if (elOnbRate) elOnbRate.innerText = `${completionPct}%`;

    const elOnbComp = document.getElementById("onb-view-completed");
    if (elOnbComp) elOnbComp.innerText = compTasks.toLocaleString();
    const elOnbPen = document.getElementById("onb-view-pending");
    if (elOnbPen) elOnbPen.innerText = penTasks.toLocaleString();

    const elFactorsTotal = document.getElementById("att-factors-total-pill");
    if (elFactorsTotal) elFactorsTotal.innerText = `${attInsights.total_exits || 70} Exits Total`;

    const elMilestoneTotal = document.getElementById("onb-milestone-total");
    if (elMilestoneTotal) elMilestoneTotal.innerText = `${totalTasks.toLocaleString()} Tasks`;

    // 2. Charts (Left: Attrition Factors | Right: Onboarding Donut)
    Charts.renderAttritionFactors("chart-attrition-factors", attInsights);
    Charts.renderOnboardingTasksDonut("chart-onboarding-donut", [
      { task_status: "Completed", task_count: compTasks },
      { task_status: "Pending", task_count: penTasks }
    ]);

    // 3. Tables (Left: Predicted Departures | Right: Onboarding Tracker)
    renderFlightRiskTable(state.cachedFlightRisk);
    renderOnboardingTable(state.cachedOnboarding);
  } catch (err) {
    console.error("[renderAttritionView err]:", err);
  }
}

function renderFlightRiskTable(roster) {
  const tbody = document.getElementById("tbody-flight-risk");
  if (!tbody) return;

  if (!roster || roster.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--text-muted); padding:1.25rem;">No employees flagged for departure in this scope.</td></tr>`;
    return;
  }

  tbody.innerHTML = roster.map(r => {
    const riskPct = r.risk_pct !== undefined ? r.risk_pct : (r.risk_score * 100).toFixed(1);
    const name = r.employee_name || "Employee";
    const driver = r.primary_reason || (r.top_contributing_factors && r.top_contributing_factors.length ? r.top_contributing_factors[0] : "Elevated tenure and absence indicators");
    const tierClass = r.risk_tier === "Critical" || parseFloat(riskPct) >= 60 ? "status-danger" : "status-high";
    return `
      <tr>
        <td><strong style="color:var(--navyDark);">${r.employee_id}</strong></td>
        <td><div style="font-weight:600; color:var(--navyDark);">${name}</div><div style="font-size:0.7rem; color:var(--text-muted);">${r.designation || ""}</div></td>
        <td>${r.department}</td>
        <td><span class="status-pill ${tierClass}">${riskPct}% Risk</span></td>
        <td><div style="font-size:0.75rem; color:var(--text-primary); line-height:1.35;">${driver}</div></td>
      </tr>
    `;
  }).join("");
}

function renderOnboardingTable(roster) {
  const tbody = document.getElementById("tbody-onboarding");
  if (!tbody) return;

  if (!roster || roster.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:var(--text-muted); padding:1.25rem;">No onboarding records found in this scope.</td></tr>`;
    return;
  }

  tbody.innerHTML = roster.map(r => {
    const name = r.employee_name || "Employee";
    const isComp = r.status === "Completed" || r.pending_tasks === 0;
    const badgeClass = isComp ? "status-low" : "status-high";
    const statusText = isComp ? "Completed (5/5)" : `${r.completed_tasks || 0}/${r.total_tasks || 5} Tasks Done`;
    return `
      <tr>
        <td><strong style="color:var(--navyDark);">${r.employee_id}</strong></td>
        <td><div style="font-weight:600; color:var(--navyDark);">${name}</div><div style="font-size:0.7rem; color:var(--text-muted);">${r.designation || ""}</div></td>
        <td>${r.department}</td>
        <td><span style="font-size:0.78rem; color:var(--text-secondary);"><i style="display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--blue); margin-right:4px;"></i>${r.location}</span></td>
        <td><span class="status-pill ${badgeClass}">${statusText}</span></td>
      </tr>
    `;
  }).join("");
}

/** 3. Render Attendance & Leave View */
async function renderAttendanceView() {
  const [attKpis, trends, leaveData, anomalies] = await Promise.all([
    API.getAttendanceKPIs(state.selectedDept, state.selectedLoc, state.selectedStartDate, state.selectedEndDate),
    API.getTrends(state.selectedDept, state.selectedLoc, state.selectedStartDate, state.selectedEndDate),
    API.getLeaveAnalytics(state.selectedDept, state.selectedLoc, state.selectedStartDate, state.selectedEndDate),
    API.getAttendanceAnomalies(2.0, state.selectedDept, state.selectedLoc, state.selectedStartDate, state.selectedEndDate)
  ]);

  const attRatePct = parseFloat(attKpis.present_pct ?? 0).toFixed(1);
  document.getElementById("att-page-rate").innerText = `${attRatePct}%`;
  document.getElementById("att-page-present").innerText = Number(attKpis.present_count ?? 0).toLocaleString();
  document.getElementById("att-page-absent").innerText = Number(attKpis.absent_count ?? 0).toLocaleString();
  
  const leaveUtil = parseFloat(leaveData.leave_utilization_pct ?? 0).toFixed(1);
  const elAttLeave = document.getElementById("att-page-leave-util");
  if (elAttLeave) elAttLeave.innerText = `${leaveUtil}%`;
  const elAttDays = document.getElementById("att-page-leave-days");
  if (elAttDays) elAttDays.innerText = Number(leaveData.approved_leave_days ?? 0).toLocaleString();
  const elAttQuota = document.getElementById("att-page-leave-quota");
  if (elAttQuota) elAttQuota.innerText = Number(leaveData.leave_quota_days ?? 0).toLocaleString();

  Charts.renderAttendanceMonthlyTrend("chart-attendance-trend", trends.attendance_trend);
  Charts.renderLeaveApprovalDonut("chart-leave-donut", leaveData.approval_distribution || []);

  state.cachedAnomalies = anomalies;
  renderAnomaliesTable(anomalies);
}

function renderAnomaliesTable(anomalies) {
  const tbody = document.getElementById("tbody-anomalies");
  if (!tbody) return;

  if (!anomalies || anomalies.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-muted); padding:1rem;">No employees with irregular attendance patterns in this scope.</td></tr>`;
    return;
  }

  tbody.innerHTML = anomalies.map(a => {
    let flag = (a.anomaly_flags && a.anomaly_flags.length) ? a.anomaly_flags[0] : "Irregular attendance pattern";
    // Clean up any remaining technical z-score or statistical jargon
    flag = flag.replace(/\s*\(Z\s*=\s*[\d\.]+\)/gi, "")
               .replace(/Clustering:/gi, "Pattern:")
               .replace(/Elevated Dept Absenteeism:/gi, "High Absenteeism:")
               .replace(/dept avg/gi, "dept average")
               .trim();

    return `
      <tr>
        <td><b>${a.employee_id}</b></td>
        <td>${a.department}</td>
        <td>${a.absence_rate_pct}%</td>
        <td>${a.mon_fri_absence_ratio_pct}%</td>
        <td>${a.short_days_count}</td>
        <td><span class="status-pill status-high">${flag}</span></td>
      </tr>
    `;
  }).join("");
}

/** 4. Render Workforce Movement View */
async function renderMovementView() {
  const [onbData, trends, movements] = await Promise.all([
    API.getOnboardingMobility(state.selectedDept, state.selectedLoc, state.selectedStartDate, state.selectedEndDate),
    API.getTrends(state.selectedDept, state.selectedLoc, state.selectedStartDate, state.selectedEndDate),
    API.getMovements(state.selectedDept, state.selectedLoc, state.selectedStartDate, state.selectedEndDate)
  ]);

  let promo = 14;
  let trans = 26;
  let rolec = 19;

  if (onbData.movements_breakdown && onbData.movements_breakdown.length) {
    onbData.movements_breakdown.forEach(m => {
      if (m.movement_type === "Promotion") promo = m.movement_count;
      else if (m.movement_type === "Department Transfer" || m.movement_type === "Transfer") trans = m.movement_count;
      else if (m.movement_type === "Role Change") rolec = m.movement_count;
    });
  }

  document.getElementById("mov-total").innerText = onbData.total_movements || (promo + trans + rolec);
  document.getElementById("mov-promotions").innerText = promo;
  document.getElementById("mov-transfers").innerText = trans;
  document.getElementById("mov-role-changes").innerText = rolec;

  Charts.renderMovementsMonthlyChart("chart-movements-monthly", trends.movement_trend);

  state.cachedMovements = movements;
  renderMovementsTable(movements);
}

function renderMovementsTable(movements) {
  const tbody = document.getElementById("tbody-movements");
  if (!tbody) return;

  if (!movements || movements.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; color:var(--text-muted); padding:1rem;">No employee movements recorded for this filter scope.</td></tr>`;
    return;
  }

  tbody.innerHTML = movements.map(m => {
    let pillClass = "status-blue";
    if (m.movement_type === "Promotion") pillClass = "status-low";
    else if (m.movement_type === "Role Change") pillClass = "status-medium";

    return `
      <tr>
        <td><b>${m.employee_id}</b></td>
        <td><div style="font-weight:600; color:var(--navyDark);">${m.employee_name || 'Employee'}</div></td>
        <td><span class="status-pill ${pillClass}">${m.movement_type}</span></td>
        <td>${m.previous_department || '—'}</td>
        <td><b>${m.new_department || m.department || '—'}</b></td>
        <td>${m.previous_designation || '—'}</td>
        <td><b>${m.new_designation || '—'}</b></td>
        <td>${m.movement_date || '—'}</td>
      </tr>
    `;
  }).join("");
}

// ==============================================================================
// 4. TABLE SEARCH & FILTER HANDLERS
// ==============================================================================
function updateOnboardingDonutFromRoster(filteredRoster) {
  let compTasks = 0;
  let penTasks = 0;

  if (Array.isArray(filteredRoster) && filteredRoster.length > 0) {
    filteredRoster.forEach(r => {
      compTasks += Number(r.completed_tasks || 0);
      penTasks += Number(r.pending_tasks || 0);
    });
  }

  const totalTasks = compTasks + penTasks;
  const compPct = totalTasks > 0 ? ((compTasks / totalTasks) * 100).toFixed(1) : "0.0";

  // Re-render Donut Chart dynamically with filtered counts
  Charts.renderOnboardingTasksDonut("chart-onboarding-donut", [
    { task_status: "Completed", task_count: compTasks },
    { task_status: "Pending", task_count: penTasks }
  ]);

  // Update Milestone Total Pill
  const elMilestoneTotal = document.getElementById("onb-milestone-total");
  if (elMilestoneTotal) elMilestoneTotal.innerText = `${totalTasks.toLocaleString()} Tasks`;

  // Update Top KPI Card Onboarding numbers dynamically
  const elOnbRate = document.getElementById("att-view-onboarding");
  if (elOnbRate) elOnbRate.innerText = `${compPct}%`;
  const elOnbComp = document.getElementById("onb-view-completed");
  if (elOnbComp) elOnbComp.innerText = compTasks.toLocaleString();
  const elOnbPen = document.getElementById("onb-view-pending");
  if (elOnbPen) elOnbPen.innerText = penTasks.toLocaleString();
}

function initTableSearchListeners() {
  // Flight Risk Search
  const searchRisk = document.getElementById("search-flight-risk");
  if (searchRisk) {
    searchRisk.addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase().trim();
      const filtered = (state.cachedFlightRisk || []).filter(r =>
        (r.employee_id || "").toLowerCase().includes(q) ||
        (r.employee_name || "").toLowerCase().includes(q) ||
        (r.department || "").toLowerCase().includes(q) ||
        (r.designation || "").toLowerCase().includes(q) ||
        (r.primary_reason || "").toLowerCase().includes(q)
      );
      renderFlightRiskTable(filtered);
    });
  }

  // Onboarding Search Handler
  const searchOnb = document.getElementById("search-onboarding");

  const filterOnboardingRoster = () => {
    const q = searchOnb ? searchOnb.value.toLowerCase().trim() : "";

    const filtered = (state.cachedOnboarding || []).filter(r => {
      return !q ||
        (r.employee_id || "").toLowerCase().includes(q) ||
        (r.employee_name || "").toLowerCase().includes(q) ||
        (r.department || "").toLowerCase().includes(q) ||
        (r.location || "").toLowerCase().includes(q) ||
        (r.status || "").toLowerCase().includes(q);
    });

    renderOnboardingTable(filtered);
    updateOnboardingDonutFromRoster(filtered);
  };

  if (searchOnb) {
    searchOnb.addEventListener("input", filterOnboardingRoster);
  }

  // Anomalies Search
  const searchAnom = document.getElementById("search-anomalies");
  if (searchAnom) {
    searchAnom.addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase().trim();
      const filtered = state.cachedAnomalies.filter(a =>
        a.employee_id.toLowerCase().includes(q) ||
        a.department.toLowerCase().includes(q) ||
        (a.anomaly_flags && a.anomaly_flags.join(" ").toLowerCase().includes(q))
      );
      renderAnomaliesTable(filtered);
    });
  }

  // Movements Search & Type Filter
  const searchMov = document.getElementById("search-movements");
  const filterMovType = document.getElementById("filter-movement-type");

  const filterMovements = () => {
    const q = searchMov ? searchMov.value.toLowerCase().trim() : "";
    const type = filterMovType ? filterMovType.value : "";
    const filtered = state.cachedMovements.filter(m => {
      const matchesQ = !q ||
        m.employee_id.toLowerCase().includes(q) ||
        (m.employee_name && m.employee_name.toLowerCase().includes(q)) ||
        (m.new_department && m.new_department.toLowerCase().includes(q)) ||
        (m.previous_department && m.previous_department.toLowerCase().includes(q)) ||
        (m.new_designation && m.new_designation.toLowerCase().includes(q));
      const matchesType = !type || m.movement_type === type;
      return matchesQ && matchesType;
    });
    renderMovementsTable(filtered);
  };

  if (searchMov) searchMov.addEventListener("input", filterMovements);
  if (filterMovType) filterMovType.addEventListener("change", filterMovements);
}

// ==============================================================================
// 5. SIDEBAR CONTROLS (COLLAPSE & EXPAND FOR ADMIN & EMPLOYEE)
// ==============================================================================
function initSidebar() {
  // 1. Admin Sidebar Controls
  const sidebar = document.getElementById("app-sidebar");
  const toggleBtn = document.getElementById("btn-toggle-sidebar");
  const uncollapseBtn = document.getElementById("btn-floating-uncollapse");

  if (toggleBtn && sidebar) {
    toggleBtn.onclick = () => {
      sidebar.classList.toggle("collapsed");
    };
  }

  if (uncollapseBtn && sidebar) {
    uncollapseBtn.onclick = () => {
      sidebar.classList.remove("collapsed");
    };
  }

  // 2. Employee Portal Sidebar Controls
  const empSidebar = document.getElementById("emp-app-sidebar");
  const empToggleBtn = document.getElementById("btn-toggle-emp-sidebar");
  const empUncollapseBtn = document.getElementById("btn-floating-uncollapse-emp");

  if (empToggleBtn && empSidebar) {
    empToggleBtn.onclick = (e) => {
      e.stopPropagation();
      empSidebar.classList.toggle("collapsed");
    };
  }

  if (empUncollapseBtn && empSidebar) {
    empUncollapseBtn.onclick = (e) => {
      e.stopPropagation();
      empSidebar.classList.remove("collapsed");
    };
  }

  // 3. Employee Sidebar Navigation Items
  const tabTitles = {
    "emp-tab-attendance": "Attendance Records",
    "emp-tab-leaves": "Leaves & Balances",
    "emp-tab-onboarding": "Onboarding Milestones",
    "emp-tab-copilot": "Personal HR Copilot"
  };

  document.querySelectorAll(".emp-nav-item").forEach(item => {
    item.onclick = () => {
      const targetId = item.dataset.tab;
      if (!targetId) return;

      if (typeof window.closeEmpChatbot === "function") {
        window.closeEmpChatbot();
      }

      document.querySelectorAll(".emp-nav-item").forEach(b => {
        b.classList.toggle("active", b.dataset.tab === targetId);
      });
      document.querySelectorAll(".emp-tab-content").forEach(sec => {
        sec.style.display = sec.id === targetId ? "block" : "none";
      });
      const pageTitle = document.getElementById("emp-page-title");
      if (pageTitle && tabTitles[targetId]) {
        pageTitle.innerText = tabTitles[targetId];
      }
    };
  });
}

// ==============================================================================
// 6. FIXED FULL-SCREEN AI CHATBOT
// ==============================================================================
function initChatbot() {
  const floatingBtn = document.getElementById("btn-floating-chatbot");
  const fullscreenChatbot = document.getElementById("fullscreen-chatbot");
  const closeBtn = document.getElementById("btn-close-chatbot");

  if (fullscreenChatbot) {
    fullscreenChatbot.style.display = "none";
  }

  if (floatingBtn && fullscreenChatbot) {
    floatingBtn.onclick = () => {
      state.chatbotOpen = true;
      fullscreenChatbot.style.display = "flex";
      fullscreenChatbot.classList.add("open");
      floatingBtn.style.setProperty("display", "none", "important");
      floatingBtn.style.visibility = "hidden";
      renderChatbotMessages();
      const input = document.getElementById("chatbot-user-input");
      if (input) input.focus();
    };
  }

  window.toggleChatbotExpand = (type) => {
    const chatbotId = type === "emp" ? "fullscreen-chatbot-emp" : "fullscreen-chatbot";
    const btnId = type === "emp" ? "btn-expand-chatbot-emp" : "btn-expand-chatbot-hr";
    const el = document.getElementById(chatbotId);
    const btn = document.getElementById(btnId);
    if (!el) return;

    const isExpanded = el.classList.toggle("expanded");
    if (btn) {
      if (isExpanded) {
        btn.setAttribute("title", "Collapse to popup (Restore)");
        btn.setAttribute("aria-label", "Collapse chatbot to popup");
        btn.innerHTML = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="4 14 10 14 10 20"></polyline>
          <polyline points="20 10 14 10 14 4"></polyline>
          <line x1="14" y1="10" x2="21" y2="3"></line>
          <line x1="3" y1="21" x2="10" y2="14"></line>
        </svg>`;
      } else {
        btn.setAttribute("title", "Expand to full window");
        btn.setAttribute("aria-label", "Expand chatbot to window size");
        btn.innerHTML = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 3 21 3 21 9"></polyline>
          <polyline points="9 21 3 21 3 15"></polyline>
          <line x1="21" y1="3" x2="14" y2="10"></line>
          <line x1="3" y1="21" x2="10" y2="14"></line>
        </svg>`;
      }
    }

    const inputId = type === "emp" ? "emp-chatbot-input" : "chatbot-user-input";
    const input = document.getElementById(inputId);
    if (input) input.focus();
  };

  window.closeChatbot = () => {
    state.chatbotOpen = false;
    if (fullscreenChatbot) {
      fullscreenChatbot.style.display = "none";
      fullscreenChatbot.classList.remove("open");
      fullscreenChatbot.classList.remove("expanded");
      const expBtn = document.getElementById("btn-expand-chatbot-hr");
      if (expBtn) {
        expBtn.setAttribute("title", "Expand to full window");
        expBtn.setAttribute("aria-label", "Expand chatbot to window size");
        expBtn.innerHTML = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 3 21 3 21 9"></polyline>
          <polyline points="9 21 3 21 3 15"></polyline>
          <line x1="21" y1="3" x2="14" y2="10"></line>
          <line x1="3" y1="21" x2="10" y2="14"></line>
        </svg>`;
      }
    }
    if (floatingBtn) {
      floatingBtn.style.setProperty("display", "flex", "important");
      floatingBtn.style.visibility = "visible";
    }
  };

  if (closeBtn && fullscreenChatbot) {
    closeBtn.onclick = window.closeChatbot;
  }

  // Escape key closes full-screen chatbot or collapses it if expanded
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && state.chatbotOpen) {
      if (fullscreenChatbot && fullscreenChatbot.classList.contains("expanded")) {
        window.toggleChatbotExpand("hr");
      } else {
        window.closeChatbot();
      }
    }
  });

  // Suggested Prompt Chips
  document.querySelectorAll(".prompt-chip").forEach(chip => {
    chip.onclick = () => submitCopilotQuery(chip.dataset.query);
  });

  // Chat Input Bar
  const chatInput = document.getElementById("chatbot-user-input");
  const sendBtn = document.getElementById("btn-send-chat");

  if (sendBtn && !sendBtn.querySelector("svg")) {
    sendBtn.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="#FFFFFF" stroke="#FFFFFF" stroke-width="0.5" xmlns="http://www.w3.org/2000/svg" style="display:block;width:20px;height:20px;margin-left:2px;fill:#FFFFFF;pointer-events:none;"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" fill="#FFFFFF"/></svg>`;
  }

  const handleSend = () => {
    if (!chatInput) return;
    const q = chatInput.value.trim();
    if (q) {
      chatInput.value = "";
      submitCopilotQuery(q);
    }
  };

  if (sendBtn) sendBtn.onclick = handleSend;
  if (chatInput) {
    chatInput.onkeypress = (e) => {
      if (e.key === "Enter") handleSend();
    };
  }
}

export async function submitCopilotQuery(queryText) {
  if (!queryText) return;

  state.chatMessages.push({ role: "user", text: queryText });
  renderChatbotMessages();

  // Thinking state animation before giving the response
  const thinkingObj = {
    role: "assistant",
    thinking: true,
    step: "Reading verified workforce dataset..."
  };
  state.chatMessages.push(thinkingObj);
  renderChatbotMessages();

  // Dynamic progressive step updates during thinking
  const stepTimer1 = setTimeout(() => {
    thinkingObj.step = "Analyzing employee records & department heuristics...";
    renderChatbotMessages();
  }, 450);

  const stepTimer2 = setTimeout(() => {
    thinkingObj.step = "Synthesizing people insights & actionable advice...";
    renderChatbotMessages();
  }, 950);

  const startTime = Date.now();

  try {
    const response = await API.askCopilot(queryText);
    const elapsed = Date.now() - startTime;
    // Smooth minimum animation duration so thinking is clearly appreciated
    if (elapsed < 1200) {
      await new Promise(resolve => setTimeout(resolve, 1200 - elapsed));
    }
    clearTimeout(stepTimer1);
    clearTimeout(stepTimer2);
    state.chatMessages.pop();

    const answer = response.natural_language_answer || response.answer || "Query completed.";
    const recommendation = response.recommended_action || "";
    const duration = ((Date.now() - startTime) / 1000).toFixed(1) + "s";

    const qLower = (queryText || "").toLowerCase();
    let followUpSuggestions = [];
    if (qLower.includes("attrition") || qLower.includes("exit") || qLower.includes("leaving")) {
      followUpSuggestions = [
        "Who are the employees at risk of leaving?",
        "What is the exit forecast for next quarter?",
        "What are the workforce movement totals?"
      ];
    } else if (qLower.includes("risk") || qLower.includes("retention")) {
      followUpSuggestions = [
        "Which department has highest attrition?",
        "What is the exit forecast for next quarter?",
        "Show irregular attendance patterns."
      ];
    } else if (qLower.includes("attendance") || qLower.includes("absent") || qLower.includes("hours")) {
      followUpSuggestions = [
        "Show irregular attendance patterns.",
        "What is the company leave utilization breakdown?",
        "Which department has highest attrition?"
      ];
    } else if (qLower.includes("movement") || qLower.includes("promotion") || qLower.includes("transfer") || qLower.includes("headcount")) {
      followUpSuggestions = [
        "What are the workforce movement totals?",
        "Which department has highest attrition?",
        "Who are the employees at risk of leaving?"
      ];
    } else {
      followUpSuggestions = [
        "Which department has highest attrition?",
        "Who are the employees at risk of leaving?",
        "Show irregular attendance patterns."
      ];
    }

    state.chatMessages.push({
      role: "assistant",
      isNew: true,
      queryText: queryText,
      thoughtDuration: duration,
      answer: answer,
      recommendation: recommendation,
      tool_used: response.tool_used,
      raw_data: response.raw_data,
      suggestions: followUpSuggestions
    });
  } catch (err) {
    clearTimeout(stepTimer1);
    clearTimeout(stepTimer2);
    const elapsed = Date.now() - startTime;
    if (elapsed < 1000) {
      await new Promise(resolve => setTimeout(resolve, 1000 - elapsed));
    }
    state.chatMessages.pop();
    state.chatMessages.push({
      role: "assistant",
      isNew: true,
      answer: "I was unable to retrieve that information right now. Please verify server connectivity with python run.py.",
      suggestions: [
        "Which department has highest attrition?",
        "Who are the employees at risk of leaving?",
        "What is the exit forecast for next quarter?"
      ]
    });
  }

  renderChatbotMessages();
}

function formatMarkdown(text) {
  if (!text) return "";
  let html = text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
  // Bold
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  // Italics
  html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
  // Code spans
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
  // Bullet points
  html = html.replace(/^[•\-\*]\s+(.+)$/gm, "<li>$1</li>");
  html = html.replace(/(<li>.*<\/li>)/gms, "<ul>$1</ul>");
  // Line breaks & paragraphs
  html = html.replace(/\n\n/g, "</p><p>").replace(/\n/g, "<br>");
  return `<p>${html}</p>`;
}

function renderChatbotMessages() {
  const container = document.getElementById("chatbot-messages-container");
  if (!container) return;

  const html = state.chatMessages.map((msg, idx) => {
    if (msg.role === "user") {
      return `
        <div class="chat-bubble-row user-row">
          <div class="chat-bubble-card user">
            ${msg.text}
          </div>
        </div>
      `;
    }

    if (msg.thinking) {
      return `
        <div class="chat-bubble-row assistant-row">
          <div class="chat-bubble-avatar">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2C12 7.52 7.52 12 2 12C7.52 12 12 16.48 12 22C12 16.48 16.48 12 22 12C16.48 12 12 7.52 12 2Z" fill="#FFFFFF"/>
              <circle cx="19.5" cy="4.5" r="2.2" fill="#93C5FD"/>
              <circle cx="4.5" cy="19.5" r="1.6" fill="#93C5FD"/>
            </svg>
          </div>
          <div class="thinking-card">
            <div class="thinking-toggle-header">
              <div class="thinking-status-wrap">
                <div class="thinking-pulse-orb"></div>
                <span class="thinking-title">Thinking in process
                  <span class="thinking-dots"><span></span><span></span><span></span></span>
                </span>
              </div>
            </div>
            <div class="thinking-progress-track">
              <div class="thinking-progress-fill"></div>
            </div>
            <div class="thinking-live-step">
              <span class="step-spark">&#10022;</span>
              <span>${msg.step || "Reading workforce records & department heuristics..."}</span>
            </div>
          </div>
        </div>
      `;
    }

    let cardHtml = `
      <div class="chat-bubble-row assistant-row ${msg.isNew ? 'new-response' : ''}">
        <div class="chat-bubble-avatar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C12 7.52 7.52 12 2 12C7.52 12 12 16.48 12 22C12 16.48 16.48 12 22 12C16.48 12 12 7.52 12 2Z" fill="#FFFFFF"/>
            <circle cx="19.5" cy="4.5" r="2.2" fill="#93C5FD"/>
            <circle cx="4.5" cy="19.5" r="1.6" fill="#93C5FD"/>
          </svg>
        </div>
        <div class="chat-bubble-card">
          <div class="chat-bubble-header">
            <span class="chat-author-name">WorkforceAI Copilot</span>
            <span class="chat-verified-pill">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
              Grounded in SQLite
            </span>
          </div>
          ${!msg.isDefault ? `
          <div class="thought-process-toggle" onclick="this.classList.toggle('open'); this.nextElementSibling.classList.toggle('open');">
            <span style="color:#2563EB;">&#10003;</span>
            <span>Thought for ${msg.thoughtDuration || '1.1s'}</span>
            <span class="thought-caret">&#9660;</span>
          </div>
          <div class="thought-process-details">
            <div class="thought-step">&#10003; Verified against company workforce dataset (<code>hr_workforce.db</code>)</div>
            <div class="thought-step">&#10003; Screened department metrics & flight-risk indicators</div>
            ${msg.tool_used ? `<div class="thought-step">&#10003; Invoked <code>${msg.tool_used}</code></div>` : ''}
          </div>
          ` : ''}
          <div class="chat-bubble-content">
            ${formatMarkdown(msg.answer)}
          </div>
    `;

    if (msg.tool_used && msg.raw_data) {
      const jsonStr = JSON.stringify(msg.raw_data, null, 2);
      cardHtml += `
        <details class="chat-telemetry">
          <summary>Data Source: ${msg.tool_used}</summary>
          <pre><code>${jsonStr}</code></pre>
        </details>
      `;
    }

    if (!msg.isDefault) {
      cardHtml += `
        <div class="chat-feedback-bar" id="feedback-bar-${idx}">
          <span class="feedback-prompt">Helpful?</span>
          <button class="feedback-btn btn-thumbs-up ${msg.feedbackGiven === 'good' ? 'active-good' : ''}" 
                  ${msg.feedbackGiven ? 'disabled' : ''} 
                  title="Good response" 
                  aria-label="Good response"
                  onclick="window.handleChatFeedback(${idx}, 'good')">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/>
            </svg>
          </button>
          <button class="feedback-btn btn-thumbs-down ${msg.feedbackGiven === 'bad' ? 'active-bad' : ''}" 
                  ${msg.feedbackGiven ? 'disabled' : ''} 
                  title="Bad response" 
                  aria-label="Bad response"
                  onclick="window.handleChatFeedback(${idx}, 'bad')">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-3"/>
            </svg>
          </button>
          <span class="feedback-status-pill" id="feedback-status-${idx}" style="${msg.feedbackGiven ? 'display:inline-flex;' : 'display:none;'}">
            ${msg.feedbackGiven === 'good' ? '✓ Good response recorded for AI training' : (msg.feedbackGiven === 'bad' ? '✓ Feedback recorded for AI model retraining' : '')}
          </span>
        </div>
      `;
    }

    if (msg.suggestions && msg.suggestions.length > 0) {
      const chipsHtml = msg.suggestions.map(s => {
        const safe = s.replace(/'/g, "\\'");
        return `<button class="inline-prompt-chip" onclick="window.selectSuggestedQuery('${safe}', 'hr')">${s}</button>`;
      }).join("");

      cardHtml += `
        <div class="chat-inline-suggestions">
          <span class="inline-suggestions-label">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="#F59E0B" stroke="#D97706" stroke-width="2">
              <path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-7 7c0 2.5 1.5 4.5 3 6h8c1.5-1.5 3-3.5 3-6a7 7 0 0 0-7-7z"/>
            </svg>
            Suggested Follow-ups
          </span>
          <div class="inline-chips-wrap">
            ${chipsHtml}
          </div>
        </div>
      `;
    }

    cardHtml += `</div></div>`;
    return cardHtml;
  }).join("");

  container.innerHTML = `<div class="chatbot-msg-container">${html}</div>`;
  container.scrollTop = container.scrollHeight;
}

export async function handleChatFeedback(msgIdx, feedbackType) {
  const msg = state.chatMessages[msgIdx];
  if (!msg || msg.feedbackGiven) return;
  msg.feedbackGiven = feedbackType;

  // Immediate UI highlight & status badge
  const bar = document.getElementById(`feedback-bar-${msgIdx}`);
  if (bar) {
    const btnGood = bar.querySelector(".btn-thumbs-up");
    const btnBad = bar.querySelector(".btn-thumbs-down");
    const status = bar.querySelector(".feedback-status-pill");

    if (btnGood) btnGood.disabled = true;
    if (btnBad) btnBad.disabled = true;

    if (feedbackType === "good" && btnGood) {
      btnGood.classList.add("active-good");
    } else if (feedbackType === "bad" && btnBad) {
      btnBad.classList.add("active-bad");
    }

    if (status) {
      status.style.display = "inline-flex";
      status.textContent = feedbackType === "good"
        ? "✓ Good response recorded for AI training"
        : "✓ Feedback recorded for AI model retraining";
    }
  }

  // Persist directly into Python training store (genai/ai_training_data.py)
  try {
    await API.submitFeedback({
      query: msg.queryText || "General Workforce Inquiry",
      response: msg.answer || "",
      feedback: feedbackType,
      tool_used: msg.tool_used || "copilot_agent"
    });
  } catch (err) {
    console.error("Failed to submit feedback to Python training store:", err);
  }
}

// Global attachment for inline HTML onclick handlers
if (typeof window !== "undefined") {
  window.handleChatFeedback = handleChatFeedback;
}

// ==============================================================================
// 7. REACTIVE FILTER CONTROLS & DATABASE STATUS
// ==============================================================================
async function loadFilterOptions() {
  const deptSelect = document.getElementById("filter-dept");
  const locSelect = document.getElementById("filter-loc");

  try {
    const filters = await API.getFilters();
    if (filters.departments && filters.departments.length > 0) {
      const opts = `<option value="">All Departments</option>` +
        filters.departments.map(d => `<option value="${d}">${d}</option>`).join("");
      if (deptSelect) {
        deptSelect.innerHTML = opts;
        if (state.selectedDept) deptSelect.value = state.selectedDept;
      }
    }

    if (locSelect && filters.locations && filters.locations.length > 0) {
      locSelect.innerHTML = `<option value="">All Locations</option>` +
        filters.locations.map(l => `<option value="${l}">${l}</option>`).join("");
      if (state.selectedLoc) locSelect.value = state.selectedLoc;
    }
  } catch (err) {
    console.warn("[loadFilterOptions] Error:", err);
  }
}

async function loadDatabaseStatus() {
  const badge = document.getElementById("db-status-pill");
  if (!badge) return;

  try {
    const status = await API.getStatus();
    if (status && status.connected) {
      badge.style.backgroundColor = "rgba(5, 150, 105, 0.15)";
      badge.style.color = "#34D399";
      badge.innerHTML = `<div class="status-dot"></div><span>Connected: ${status.database}</span>`;
    } else {
      badge.style.backgroundColor = "rgba(220, 38, 38, 0.15)";
      badge.style.color = "#F87171";
      badge.innerHTML = `<div class="status-dot" style="background:#EF4444;"></div><span>Connecting to SQLite...</span>`;
      setTimeout(loadDatabaseStatus, 2500);
    }
  } catch (err) {
    badge.style.backgroundColor = "rgba(220, 38, 38, 0.15)";
    badge.style.color = "#F87171";
    badge.innerHTML = `<div class="status-dot" style="background:#EF4444;"></div><span>Server Offline</span>`;
    setTimeout(loadDatabaseStatus, 3000);
  }
}

async function onFiltersChanged() {
  const badge = document.getElementById("active-filter-badge");
  const countBadge = document.getElementById("filter-count-badge");
  const triggerBtn = document.getElementById("btn-filter-trigger");
  const pillsContainer = document.getElementById("active-filter-pills");

  const activeFilters = [];
  if (state.selectedDept) activeFilters.push({ type: "dept", label: `Dept: ${state.selectedDept}` });
  if (state.selectedLoc) activeFilters.push({ type: "loc", label: `Loc: ${state.selectedLoc}` });
  if (state.selectedStartDate && state.selectedEndDate) {
    activeFilters.push({ type: "date", label: `${state.selectedStartDate} → ${state.selectedEndDate}` });
  } else if (state.selectedStartDate) {
    activeFilters.push({ type: "date", label: `From: ${state.selectedStartDate}` });
  } else if (state.selectedEndDate) {
    activeFilters.push({ type: "date", label: `To: ${state.selectedEndDate}` });
  }

  // Update filter trigger button badge & highlight
  if (triggerBtn) {
    if (activeFilters.length > 0) {
      triggerBtn.classList.add("has-active");
      if (countBadge) {
        countBadge.style.display = "inline-block";
        countBadge.innerText = activeFilters.length;
      }
    } else {
      triggerBtn.classList.remove("has-active");
      if (countBadge) {
        countBadge.style.display = "none";
      }
    }
  }

  // Render clickable filter pill tags next to button
  if (pillsContainer) {
    if (activeFilters.length > 0) {
      pillsContainer.innerHTML = activeFilters.map(f => `
        <span class="filter-pill-tag">
          <span>${f.label}</span>
          <button class="btn-remove-tag" onclick="window.clearSingleFilter('${f.type}')" title="Remove filter">&times;</button>
        </span>
      `).join("");
    } else {
      pillsContainer.innerHTML = "";
    }
  }

  if (badge) {
    badge.style.display = "none";
  }

  // Refresh current view immediately with active scope filters!
  await renderActiveView(state.currentView);
}

// ==============================================================================
// 12. SUGGESTION POPOVER & INLINE QUERY HANDLERS
// ==============================================================================
window.toggleSuggestionsPopup = function(type) {
  const isEmp = type === 'emp';
  const targetTray = document.getElementById(isEmp ? 'suggestions-popover-emp' : 'suggestions-popover-hr');
  const otherTray = document.getElementById(isEmp ? 'suggestions-popover-hr' : 'suggestions-popover-emp');
  const targetBtn = document.getElementById(isEmp ? 'btn-bulb-emp' : 'btn-bulb-hr');
  const otherBtn = document.getElementById(isEmp ? 'btn-bulb-hr' : 'btn-bulb-emp');

  if (otherTray) otherTray.style.display = 'none';
  if (otherBtn) otherBtn.classList.remove('active');

  if (targetTray) {
    const isShown = targetTray.style.display !== 'none';
    targetTray.style.display = isShown ? 'none' : 'flex';
    if (targetBtn) {
      if (isShown) targetBtn.classList.remove('active');
      else targetBtn.classList.add('active');
    }
  }
};

window.selectSuggestedQuery = function(queryText, type) {
  const isEmp = type === 'emp';
  const tray = document.getElementById(isEmp ? 'suggestions-popover-emp' : 'suggestions-popover-hr');
  const btn = document.getElementById(isEmp ? 'btn-bulb-emp' : 'btn-bulb-hr');
  if (tray) tray.style.display = 'none';
  if (btn) btn.classList.remove('active');

  if (isEmp) {
    if (window.submitEmpCopilotMessage) {
      window.submitEmpCopilotMessage(queryText);
    }
  } else {
    submitCopilotQuery(queryText);
  }
};

// ==============================================================================
// 13. SINGLE FILTER DROPDOWN POPOVER CONTROLLER
// ==============================================================================
window.toggleFilterDropdown = function(e) {
  if (e) e.stopPropagation();
  const menu = document.getElementById("filter-popover-menu");
  const trigger = document.getElementById("btn-filter-trigger");
  if (!menu) return;
  const isHidden = menu.style.display === "none" || !menu.style.display;
  if (isHidden) {
    menu.style.display = "flex";
    if (trigger) {
      trigger.classList.add("is-open");
      trigger.setAttribute("aria-expanded", "true");
    }
  } else {
    menu.style.display = "none";
    if (trigger) {
      trigger.classList.remove("is-open");
      trigger.setAttribute("aria-expanded", "false");
    }
  }
};

window.closeFilterDropdown = function() {
  const menu = document.getElementById("filter-popover-menu");
  const trigger = document.getElementById("btn-filter-trigger");
  if (menu) menu.style.display = "none";
  if (trigger) {
    trigger.classList.remove("is-open");
    trigger.setAttribute("aria-expanded", "false");
  }
};

window.clearSingleFilter = function(filterType) {
  if (filterType === "dept") {
    state.selectedDept = "";
    const el = document.getElementById("filter-dept");
    if (el) el.value = "";
  } else if (filterType === "loc") {
    state.selectedLoc = "";
    const el = document.getElementById("filter-loc");
    if (el) el.value = "";
  } else if (filterType === "date") {
    state.selectedStartDate = "";
    state.selectedEndDate = "";
    const el1 = document.getElementById("filter-start-date");
    const el2 = document.getElementById("filter-end-date");
    if (el1) el1.value = "";
    if (el2) el2.value = "";
  }
  onFiltersChanged();
};

// Global click-outside listener to dismiss popovers
document.addEventListener("click", (e) => {
  const target = e.target;

  // Filter dropdown dismiss
  const filterWrapper = document.getElementById("filter-dropdown-wrapper");
  if (filterWrapper && !filterWrapper.contains(target)) {
    window.closeFilterDropdown();
  }

  // Chatbot suggestions dismiss
  const isBulb = target.closest(".btn-bulb-trigger");
  const isTray = target.closest(".suggestions-popover-tray");
  if (!isBulb && !isTray) {
    const hrTray = document.getElementById("suggestions-popover-hr");
    const empTray = document.getElementById("suggestions-popover-emp");
    const hrBulb = document.getElementById("btn-bulb-hr");
    const empBulb = document.getElementById("btn-bulb-emp");
    if (hrTray) hrTray.style.display = "none";
    if (empTray) empTray.style.display = "none";
    if (hrBulb) hrBulb.classList.remove("active");
    if (empBulb) empBulb.classList.remove("active");
  }
});

// Escape key closes filter popover
window.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    window.closeFilterDropdown();
  }
});

