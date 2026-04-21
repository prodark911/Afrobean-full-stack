import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts";

export default function Login() {
  const { login, requestOtp, verifyOtp, signup } = useAuth();
  const nav = useNavigate();
  const [mode, setMode] = useState("login"); // login | signup | otp
  const [f, setF] = useState({ email: "demo@afrobean.co.uk", password: "Demo@123", name: "", code: "" });
  const [err, setErr] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [devCode, setDevCode] = useState("");

  const submit = async (e) => {
    e.preventDefault(); setErr("");
    try {
      if (mode === "login") await login(f.email, f.password);
      else if (mode === "signup") await signup({ email: f.email, password: f.password, name: f.name });
      else if (mode === "otp") {
        if (!otpSent) {
          const r = await requestOtp(f.email);
          setOtpSent(true); setDevCode(r.dev_code || "");
          return;
        }
        await verifyOtp(f.email, f.code);
      }
      nav("/account");
    } catch (e) { setErr(e.response?.data?.detail || "Something went wrong"); }
  };

  return (
    <div className="max-w-md mx-auto px-4 py-16" data-testid="login-page">
      <h1 className="font-display text-4xl text-center">Welcome to Afrobean</h1>
      <p className="text-center text-afro-ink-soft mt-2">Sign in to save baskets, reorder and get WhatsApp updates.</p>
      <div className="grid grid-cols-3 gap-2 mt-8 bg-afro-surface-alt p-1 rounded-lg text-sm">
        {["login", "signup", "otp"].map(m => (
          <button key={m} onClick={() => { setMode(m); setOtpSent(false); setErr(""); }} className={`py-2 rounded-md font-medium ${mode === m ? "bg-white shadow-card" : "text-afro-ink-soft"}`} data-testid={`tab-${m}`}>
            {m === "login" ? "Sign in" : m === "signup" ? "Create account" : "Email OTP"}
          </button>
        ))}
      </div>
      <form onSubmit={submit} className="mt-6 space-y-4 bg-white border border-afro-border rounded-2xl p-6" data-testid="login-form">
        {mode === "signup" && (
          <label className="block"><span className="text-sm">Full name</span>
            <input required value={f.name} onChange={e => setF({ ...f, name: e.target.value })} className="afr-input" data-testid="signup-name" />
          </label>
        )}
        <label className="block"><span className="text-sm">Email</span>
          <input type="email" required value={f.email} onChange={e => setF({ ...f, email: e.target.value })} className="afr-input" data-testid="auth-email" />
        </label>
        {mode !== "otp" && (
          <label className="block"><span className="text-sm">Password</span>
            <input type="password" required value={f.password} onChange={e => setF({ ...f, password: e.target.value })} className="afr-input" data-testid="auth-password" />
          </label>
        )}
        {mode === "otp" && otpSent && (
          <label className="block"><span className="text-sm">6-digit code</span>
            <input required value={f.code} onChange={e => setF({ ...f, code: e.target.value })} className="afr-input tracking-[0.5em] text-center font-mono" placeholder="000000" maxLength={6} data-testid="otp-code" />
            {devCode && <span className="text-xs text-afro-ink-soft">Dev code: <span className="font-mono font-semibold">{devCode}</span></span>}
          </label>
        )}
        {err && <p className="text-sm text-afro-error">{err}</p>}
        <button type="submit" className="afr-btn-primary w-full" data-testid="auth-submit">
          {mode === "login" ? "Sign in" : mode === "signup" ? "Create account" : (otpSent ? "Verify code" : "Send code")}
        </button>
        <div className="text-xs text-afro-ink-soft text-center">Demo: <b>demo@afrobean.co.uk</b> / <b>Demo@123</b></div>
      </form>
    </div>
  );
}
