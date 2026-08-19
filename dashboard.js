if (!getToken()) window.location.href = "index.html";

const user = getCurrentUser();
document.getElementById("user-name").textContent = user ? `Hi, ${user.fullName}` : "";

document.getElementById("logout-btn").addEventListener("click", () => {
  clearSession();
  window.location.href = "index.html";
});

document.querySelectorAll("[data-modal]").forEach((btn) => {
  btn.addEventListener("click", () => document.getElementById(btn.dataset.modal).classList.add("open"));
});
document.querySelectorAll("[data-close]").forEach((btn) => {
  btn.addEventListener("click", () => document.getElementById(btn.dataset.close).classList.remove("open"));
});

const money = (n) => `R${Number(n).toLocaleString("en-ZA", { minimumFractionDigits: 2 })}`;

async function loadDashboard() {
  const stats = await api.getDashboard();
  const grid = document.getElementById("stats-grid");
  grid.innerHTML = `
    <div class="stat-card"><div class="value">${stats.totalProperties}</div><div class="label">Properties</div></div>
    <div class="stat-card"><div class="value">${stats.totalTenants}</div><div class="label">Tenants</div></div>
    <div class="stat-card overdue"><div class="value">${stats.totalOverdue}</div><div class="label">Overdue Payments</div></div>
    <div class="stat-card paid"><div class="value">${stats.totalPaid}</div><div class="label">Paid This Cycle</div></div>
  `;
}

async function loadProperties() {
  const properties = await api.getProperties();
  const list = document.getElementById("properties-list");
  list.innerHTML = properties.length
    ? properties.map((p) => `
      <div class="item-card">
        <div>
          <div class="main-info">${p.name}</div>
          <div class="sub-info">${p.address}${p.city ? `, ${p.city}` : ""} · ${p.tenantCount} tenant(s)</div>
        </div>
        <button class="cancel-btn" onclick="removeProperty(${p.id})">Delete</button>
      </div>`).join("")
    : `<p class="empty-state">No properties yet. Add your first one above.</p>`;

  const select = document.getElementById("tenant-property");
  select.innerHTML = properties.map((p) => `<option value="${p.id}">${p.name}</option>`).join("");
}

window.removeProperty = async (id) => {
  if (!confirm("Delete this property and all its tenants?")) return;
  await api.deleteProperty(id);
  await Promise.all([loadProperties(), loadTenants(), loadDashboard()]);
};

document.getElementById("property-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  await api.createProperty({
    name: document.getElementById("property-name").value.trim(),
    address: document.getElementById("property-address").value.trim(),
    city: document.getElementById("property-city").value.trim(),
    province: document.getElementById("property-province").value.trim(),
  });
  e.target.reset();
  document.getElementById("property-modal").classList.remove("open");
  await Promise.all([loadProperties(), loadDashboard()]);
});

async function loadTenants(search = "") {
  const tenants = await api.getTenants(search);
  const list = document.getElementById("tenants-list");
  list.innerHTML = tenants.length
    ? tenants.map((t) => `
      <div class="item-card">
        <div>
          <div class="main-info">${t.fullName} ${t.unitNumber ? `· Unit ${t.unitNumber}` : ""}</div>
          <div class="sub-info">${t.propertyName} · ${money(t.monthlyRent)}/mo · due day ${t.rentDueDay}</div>
        </div>
        <button class="cancel-btn" onclick="removeTenant(${t.id})">Delete</button>
      </div>`).join("")
    : `<p class="empty-state">No tenants yet.</p>`;

  const select = document.getElementById("payment-tenant");
  select.innerHTML = tenants.map((t) => `<option value="${t.id}" data-rent="${t.monthlyRent}">${t.fullName} (${t.propertyName})</option>`).join("");
}

window.removeTenant = async (id) => {
  if (!confirm("Delete this tenant?")) return;
  await api.deleteTenant(id);
  await Promise.all([loadTenants(), loadProperties(), loadDashboard()]);
};

document.getElementById("tenant-search").addEventListener("input", (e) => loadTenants(e.target.value));

document.getElementById("tenant-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  await api.createTenant({
    propertyId: Number(document.getElementById("tenant-property").value),
    fullName: document.getElementById("tenant-name").value.trim(),
    email: document.getElementById("tenant-email").value.trim(),
    phone: document.getElementById("tenant-phone").value.trim(),
    unitNumber: document.getElementById("tenant-unit").value.trim(),
    monthlyRent: Number(document.getElementById("tenant-rent").value),
    rentDueDay: Number(document.getElementById("tenant-due-day").value),
  });
  e.target.reset();
  document.getElementById("tenant-modal").classList.remove("open");
  await Promise.all([loadTenants(), loadProperties(), loadDashboard()]);
});

document.getElementById("payment-tenant").addEventListener("change", (e) => {
  const opt = e.target.selectedOptions[0];
  if (opt) document.getElementById("payment-amount").value = opt.dataset.rent;
});

async function loadPayments(status = "") {
  const payments = await api.getPayments(status);
  const list = document.getElementById("payments-list");
  list.innerHTML = payments.length
    ? payments.map((p) => `
      <div class="item-card">
        <div>
          <div class="main-info">${p.tenantName} — ${money(p.amountDue)}</div>
          <div class="sub-info">Due ${p.dueDate} ${p.paidDate ? `· Paid ${p.paidDate}` : ""}</div>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <span class="badge ${p.status}">${p.status}</span>
          ${p.status !== "paid" ? `<button class="mark-paid-btn" onclick="markPaid(${p.id})">Mark Paid</button>` : ""}
        </div>
      </div>`).join("")
    : `<p class="empty-state">No payments recorded yet.</p>`;
}

window.markPaid = async (id) => {
  await api.markPaid(id);
  await Promise.all([loadPayments(document.getElementById("payment-filter").value), loadDashboard()]);
};

document.getElementById("payment-filter").addEventListener("change", (e) => loadPayments(e.target.value));

document.getElementById("payment-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  await api.createPayment({
    tenantId: Number(document.getElementById("payment-tenant").value),
    amountDue: Number(document.getElementById("payment-amount").value),
    dueDate: document.getElementById("payment-due-date").value,
  });
  e.target.reset();
  document.getElementById("payment-modal").classList.remove("open");
  await Promise.all([loadPayments(), loadDashboard()]);
});

(async function init() {
  try {
    await Promise.all([loadDashboard(), loadProperties(), loadTenants(), loadPayments()]);
  } catch (err) {
    console.error(err);
  }
})();