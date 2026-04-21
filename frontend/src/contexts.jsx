import React, { createContext, useContext, useEffect, useState } from "react";
import { api, getGuestSession } from "./api";

// --------- Customer Auth ----------
const AuthCtx = createContext(null);
export function useAuth() { return useContext(AuthCtx); }

export function AuthProvider({ children }) {
  const [customer, setCustomer] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getGuestSession();
    const token = localStorage.getItem("afr_token");
    if (!token) { setLoading(false); return; }
    api.get("/me").then(r => setCustomer(r.data)).catch(() => {
      localStorage.removeItem("afr_token");
    }).finally(() => setLoading(false));
  }, []);

  const login = async (email, password) => {
    const { data } = await api.post("/auth/login", { email, password });
    localStorage.setItem("afr_token", data.token);
    setCustomer(data.customer);
    return data;
  };
  const signup = async (payload) => {
    const { data } = await api.post("/auth/signup", payload);
    localStorage.setItem("afr_token", data.token);
    setCustomer(data.customer);
    return data;
  };
  const requestOtp = (email) => api.post("/auth/otp/request", { email }).then(r => r.data);
  const verifyOtp = async (email, code) => {
    const { data } = await api.post("/auth/otp/verify", { email, code });
    localStorage.setItem("afr_token", data.token);
    setCustomer(data.customer);
    return data;
  };
  const logout = () => {
    localStorage.removeItem("afr_token");
    setCustomer(null);
  };
  return <AuthCtx.Provider value={{ customer, setCustomer, loading, login, signup, requestOtp, verifyOtp, logout }}>{children}</AuthCtx.Provider>;
}

// --------- Admin Auth ----------
const AdminCtx = createContext(null);
export function useAdmin() { return useContext(AdminCtx); }

export function AdminProvider({ children }) {
  const [admin, setAdmin] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("afr_admin_token");
    if (!token) { setLoading(false); return; }
    // temp swap auth header
    const original = localStorage.getItem("afr_token");
    localStorage.removeItem("afr_token");
    api.get("/admin/me", { headers: { Authorization: `Bearer ${token}` } })
      .then(r => setAdmin(r.data))
      .catch(() => localStorage.removeItem("afr_admin_token"))
      .finally(() => {
        if (original) localStorage.setItem("afr_token", original);
        setLoading(false);
      });
  }, []);

  const login = async (email, password) => {
    const { data } = await api.post("/admin/auth/login", { email, password });
    localStorage.setItem("afr_admin_token", data.token);
    setAdmin(data.user);
    return data;
  };
  const logout = () => {
    localStorage.removeItem("afr_admin_token");
    setAdmin(null);
  };
  return <AdminCtx.Provider value={{ admin, setAdmin, loading, login, logout }}>{children}</AdminCtx.Provider>;
}

// --------- Cart ----------
const CartCtx = createContext(null);
export function useCart() { return useContext(CartCtx); }

export function CartProvider({ children }) {
  const [cart, setCart] = useState({ items: [], subtotal: 0 });
  const [drawerOpen, setDrawerOpen] = useState(false);

  const refresh = async () => {
    try {
      const { data } = await api.get("/cart");
      setCart(data || { items: [], subtotal: 0 });
    } catch { /* ignore */ }
  };

  useEffect(() => { refresh(); }, []);

  const add = async (product_id, variant_sku = null, quantity = 1) => {
    const { data } = await api.post("/cart/add", { product_id, variant_sku, quantity });
    setCart(data);
    setDrawerOpen(true);
    return data;
  };
  const update = async (product_id, variant_sku, quantity) => {
    const { data } = await api.post("/cart/update", { product_id, variant_sku, quantity });
    setCart(data);
  };
  const remove = async (product_id, variant_sku) => {
    const { data } = await api.post("/cart/update", { product_id, variant_sku, quantity: 0 });
    setCart(data);
  };
  const bulkAdd = async (items) => {
    const { data } = await api.post("/cart/bulk-add", { items });
    setCart(data);
    setDrawerOpen(true);
  };
  const clear = async () => {
    await api.post("/cart/clear");
    refresh();
  };
  const count = cart.items?.reduce((a, b) => a + b.quantity, 0) || 0;
  return (
    <CartCtx.Provider value={{ cart, refresh, add, update, remove, bulkAdd, clear, count, drawerOpen, setDrawerOpen }}>
      {children}
    </CartCtx.Provider>
  );
}
