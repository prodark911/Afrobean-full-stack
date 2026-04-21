import axios from "axios";

const BASE = process.env.REACT_APP_BACKEND_URL;
export const API = `${BASE}/api`;

export const api = axios.create({ baseURL: API });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("afr_token") || localStorage.getItem("afr_admin_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  const sid = localStorage.getItem("afr_session");
  if (sid && !config.params?.session_id) {
    config.params = { ...(config.params || {}), session_id: sid };
  }
  return config;
});

export function getGuestSession() {
  let sid = localStorage.getItem("afr_session");
  if (!sid) {
    sid = crypto.randomUUID();
    localStorage.setItem("afr_session", sid);
  }
  return sid;
}

export function formatGBP(n) {
  if (n === null || n === undefined || isNaN(n)) return "£0.00";
  return new Intl.NumberFormat("en-GB", { style: "currency", currency: "GBP" }).format(n);
}
