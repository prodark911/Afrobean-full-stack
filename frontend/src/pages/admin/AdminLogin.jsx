import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAdmin } from "../../contexts";

export default function AdminLogin() {
  const { login } = useAdmin();
  const nav = useNavigate();
  const [f, setF] = useState({ email: "admin@afrobean.co.uk", password: "Admin@123" });
  const [err, setErr] = useState(""); const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault(); setErr(""); setLoading(true);
    try { await login(f.email, f.password); nav("/admin/dashboard"); }
    catch (e) { setErr(e.response?.data?.detail || "Login failed"); }
    finally { setLoading(false); }
  };
  return (
    <div className="admin-scope min-h-screen flex items-center justify-center p-6" data-testid="admin-login-page">
      <form onSubmit={submit} className="bg-white rounded-xl border border-admin-border p-8 w-full max-w-md font-admin">
        <div className="flex items-center gap-2 mb-6">
          <div className="w-9 h-9 rounded bg-afro-primary flex items-center justify-center text-white font-display font-bold">A</div>
          <div>
            <div className="font-semibold">Afrobean Admin</div>
            <div className="text-xs text-gray-500">Sign in to continue</div>
          </div>
        </div>
        <label className="block mb-3"><span className="text-xs text-gray-700">Email</span>
          <input type="email" required value={f.email} onChange={e => setF({ ...f, email: e.target.value })} className="afr-input mt-1" data-testid="admin-email" />
        </label>
        <label className="block mb-4"><span className="text-xs text-gray-700">Password</span>
          <input type="password" required value={f.password} onChange={e => setF({ ...f, password: e.target.value })} className="afr-input mt-1" data-testid="admin-password" />
        </label>
        {err && <p className="text-xs text-red-600 mb-3">{err}</p>}
        <button type="submit" disabled={loading} className="w-full bg-gray-900 text-white py-2 rounded-md text-sm font-medium hover:bg-gray-800 disabled:opacity-60" data-testid="admin-submit">{loading ? "Signing in…" : "Sign in"}</button>
        <p className="text-xs text-gray-500 mt-4 text-center">Default: admin@afrobean.co.uk / Admin@123</p>
      </form>
    </div>
  );
}
