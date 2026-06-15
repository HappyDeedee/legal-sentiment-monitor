(() => {
  const root = window;
  const doc = document;
  let toastTimer = null;

  function resolveTarget(target) {
    if (!target) return null;
    return typeof target === "string" ? doc.querySelector(target) : target;
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, (char) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    }[char]));
  }

  function showToast(message, type = "info", options = {}) {
    const el = doc.getElementById(options.id || "toast");
    if (!el) return null;
    if (toastTimer) clearTimeout(toastTimer);
    el.textContent = String(message || "");
    el.className = `toast active ${type || "info"}`;
    el.setAttribute("role", "status");
    el.setAttribute("aria-live", "polite");
    const timeout = Number(options.timeoutMs || 3500);
    toastTimer = setTimeout(() => {
      el.classList.remove("active", "ok", "success", "warn", "warning", "danger", "error", "info");
      el.style.display = "";
    }, timeout);
    return el;
  }

  function showLoading(target, options = {}) {
    const el = resolveTarget(target);
    if (!el) return () => {};
    const label = options.label || "加载中...";
    el.dataset.monitorLoadingPrevious = el.getAttribute("aria-busy") || "";
    el.setAttribute("aria-busy", "true");
    el.classList.add("is-loading");
    if (options.replaceContent) {
      el.dataset.monitorLoadingHtml = el.innerHTML;
      el.innerHTML = `<div class="monitor-loading"><span class="monitor-spinner" aria-hidden="true"></span><span>${label}</span></div>`;
    }
    return () => hideLoading(el);
  }

  function hideLoading(target) {
    const el = resolveTarget(target);
    if (!el) return;
    const previous = el.dataset.monitorLoadingPrevious;
    if (previous) el.setAttribute("aria-busy", previous);
    else el.removeAttribute("aria-busy");
    if (Object.prototype.hasOwnProperty.call(el.dataset, "monitorLoadingHtml")) {
      el.innerHTML = el.dataset.monitorLoadingHtml;
      delete el.dataset.monitorLoadingHtml;
    }
    delete el.dataset.monitorLoadingPrevious;
    el.classList.remove("is-loading");
  }

  function renderEmptyState(target, options = {}) {
    const el = resolveTarget(target);
    if (!el) return null;
    const title = escapeHtml(options.title || "暂无数据");
    const description = escapeHtml(options.description || "");
    const action = options.actionHtml || "";
    el.innerHTML = `<div class="empty-state" role="status"><strong>${title}</strong>${description ? `<span>${description}</span>` : ""}${action}</div>`;
    return el.firstElementChild;
  }

  function ensurePortalRoot() {
    let rootEl = doc.getElementById("monitor_portal_root");
    if (!rootEl) {
      rootEl = doc.createElement("div");
      rootEl.id = "monitor_portal_root";
      rootEl.className = "monitor-portal-root";
      doc.body.appendChild(rootEl);
    }
    return rootEl;
  }

  function closeFloatingMenus() {
    doc.dispatchEvent(new CustomEvent("monitor:close-floating-menus"));
  }

  function positionFloatingMenu(triggerEl, menuEl, options = {}) {
    const trigger = resolveTarget(triggerEl);
    const menu = resolveTarget(menuEl);
    if (!trigger || !menu) return null;

    const margin = Number(options.margin || 12);
    const gap = Number(options.gap || 6);
    const rect = trigger.getBoundingClientRect();
    menu.classList.add("is-floating");
    menu.style.position = "fixed";
    menu.style.right = "auto";
    menu.style.bottom = "auto";
    menu.style.visibility = "hidden";
    menu.style.left = "0px";
    menu.style.top = "0px";

    const menuWidth = menu.offsetWidth || Number(options.width || 168);
    const menuHeight = menu.offsetHeight || Number(options.height || 160);
    const viewportWidth = root.innerWidth || doc.documentElement.clientWidth || 0;
    const viewportHeight = root.innerHeight || doc.documentElement.clientHeight || 0;
    const preferredLeft = options.align === "left" ? rect.left : rect.right - menuWidth;
    const maxLeft = Math.max(margin, viewportWidth - menuWidth - margin);
    const left = Math.max(margin, Math.min(maxLeft, preferredLeft));
    const belowTop = rect.bottom + gap;
    const aboveTop = rect.top - menuHeight - gap;
    const top = belowTop + menuHeight + margin <= viewportHeight
      ? belowTop
      : Math.max(margin, Math.min(viewportHeight - menuHeight - margin, aboveTop));

    menu.style.left = `${Math.round(left)}px`;
    menu.style.top = `${Math.round(top)}px`;
    menu.style.visibility = "";
    return { left, top, width: menuWidth, height: menuHeight };
  }

  root.MonitorUI = Object.freeze({
    showToast,
    showLoading,
    hideLoading,
    renderEmptyState,
    closeFloatingMenus,
    positionFloatingMenu,
    ensurePortalRoot,
  });
})();
