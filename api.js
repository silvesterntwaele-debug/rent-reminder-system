const API_BASE = "http://127.0.0.1:5000/api";

function getToken() {
  return localStorage.getItem("token");
}

function setSession(token, user) {
  localStorage.setItem("token", token);
  localStorage.setItem("user", JSON.stringify(user));
}

function clearSession() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
}

function getCurrentUser() {
  const raw = localStorage.getItem("user");
  return raw ? JSON.parse(raw) : null;
}

async function apiRequest(path, { method = "GET", body = null, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  });

  const data = await res.json().catch(() => ({}));

  if (res.status === 401 && auth) {
    clearSession();
    window.location.href = "index.html";
    return;
  }
  if (!res.ok) {
    throw new Error(data.error || "Something went wrong");
  }
  return data;
}

const api = {
  register: (fullName, email, password) =>
    apiRequest("/auth/register", { method: "POST", auth: false, body: { fullName, email, password } }),
  login: (email, password) =>
    apiRequest("/auth/login", { method: "POST", auth: false, body: { email, password } }),

  getProperties: () => apiRequest("/properties"),
  createProperty: (payload) => apiRequest("/properties", { method: "POST", body: payload }),
  deleteProperty: (id) => apiRequest(`/properties/${id}`, { method: "DELETE" }),

  getTenants: (search = "") => apiRequest(`/tenants${search ? `?search=${encodeURIComponent(search)}` : ""}`),
  createTenant: (payload) => apiRequest("/tenants", { method: "POST", body: payload }),
  deleteTenant: (id) => apiRequest(`/tenants/${id}`, { method: "DELETE" }),

  getPayments: (status = "") => apiRequest(`/payments${status ? `?status=${status}` : ""}`),
  createPayment: (payload) => apiRequest("/payments", { method: "POST", body: payload }),
  markPaid: (id, amountPaid) => apiRequest(`/payments/${id}/mark-paid`, { method: "POST", body: { amountPaid } }),
  deletePayment: (id) => apiRequest(`/payments/${id}`, { method: "DELETE" }),

  getDashboard: () => apiRequest("/payments/dashboard"),
};