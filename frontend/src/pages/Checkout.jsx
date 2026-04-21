import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, formatGBP } from "../api";
import { useCart, useAuth } from "../contexts";

export default function Checkout() {
  const { cart } = useCart();
  const { customer } = useAuth();
  const [form, setForm] = useState({
    name: customer?.name || "", phone: customer?.phone || "",
    line1: "", line2: "", city: "Peterborough", postcode: "",
    country: "UK", notes: "", distance_miles: 2,
  });
  const [quote, setQuote] = useState(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const nav = useNavigate();
  const subtotal = cart.items?.reduce((a, b) => a + b.price * b.quantity, 0) || 0;

  useEffect(() => {
    if (!cart.items?.length) return;
    api.post("/delivery/quote", { subtotal, distance_miles: +form.distance_miles })
      .then(r => setQuote(r.data)).catch(e => setErr(e.response?.data?.detail || "Delivery check failed"));
  }, [subtotal, form.distance_miles, cart.items?.length]);

  if (!cart.items?.length) {
    return <div className="max-w-3xl mx-auto px-4 py-20 text-center"><h1 className="font-display text-3xl">Your basket is empty</h1></div>;
  }

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true); setErr("");
    try {
      const body = {
        origin_url: window.location.origin,
        address: {
          name: form.name, line1: form.line1, line2: form.line2,
          city: form.city, postcode: form.postcode, country: form.country, phone: form.phone,
        },
        distance_miles: +form.distance_miles,
        notes: form.notes,
      };
      const { data } = await api.post("/checkout/session", body);
      window.location.href = data.url;
    } catch (e) {
      setErr(e.response?.data?.detail || "Checkout failed");
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-10" data-testid="checkout-page">
      <h1 className="font-display text-4xl md:text-5xl mb-8">Checkout</h1>
      <form onSubmit={submit} className="grid lg:grid-cols-3 gap-10">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white border border-afro-border rounded-xl p-6">
            <h2 className="font-display text-2xl mb-4">Delivery address</h2>
            <div className="grid sm:grid-cols-2 gap-4">
              <label className="block"><span className="text-sm">Full name</span>
                <input required value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} className="afr-input" data-testid="chk-name" />
              </label>
              <label className="block"><span className="text-sm">Phone</span>
                <input required value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} className="afr-input" data-testid="chk-phone" />
              </label>
              <label className="block sm:col-span-2"><span className="text-sm">Address line 1</span>
                <input required value={form.line1} onChange={e => setForm({ ...form, line1: e.target.value })} className="afr-input" data-testid="chk-line1" />
              </label>
              <label className="block sm:col-span-2"><span className="text-sm">Address line 2 <span className="text-afro-ink-soft">(optional)</span></span>
                <input value={form.line2} onChange={e => setForm({ ...form, line2: e.target.value })} className="afr-input" data-testid="chk-line2" />
              </label>
              <label className="block"><span className="text-sm">City</span>
                <input required value={form.city} onChange={e => setForm({ ...form, city: e.target.value })} className="afr-input" data-testid="chk-city" />
              </label>
              <label className="block"><span className="text-sm">Postcode</span>
                <input required value={form.postcode} onChange={e => setForm({ ...form, postcode: e.target.value })} className="afr-input" data-testid="chk-postcode" />
              </label>
              <label className="block sm:col-span-2"><span className="text-sm">Distance from our store (miles)</span>
                <input type="number" min={0} max={5} step={0.1} value={form.distance_miles} onChange={e => setForm({ ...form, distance_miles: e.target.value })} className="afr-input" data-testid="chk-distance" />
                <span className="text-xs text-afro-ink-soft">We deliver within 5 miles of 1227 Bourges Blvd, Peterborough PE1 2AU. £2.99 per mile, free over £50.</span>
              </label>
            </div>
          </div>
          <div className="bg-white border border-afro-border rounded-xl p-6">
            <h2 className="font-display text-2xl mb-4">Order notes</h2>
            <textarea value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} rows={3} className="afr-input" placeholder="Any delivery notes..." data-testid="chk-notes" />
          </div>
        </div>
        <aside className="bg-afro-surface-alt rounded-xl p-6 h-fit lg:sticky lg:top-28" data-testid="checkout-summary">
          <h3 className="font-display text-2xl mb-4">Summary</h3>
          <div className="space-y-2 max-h-56 overflow-y-auto pr-2 text-sm border-b border-afro-border pb-3">
            {cart.items.map(it => (
              <div key={`${it.product_id}-${it.variant_sku}`} className="flex justify-between">
                <span className="flex-1 truncate pr-2">{it.name} × {it.quantity}</span>
                <span>{formatGBP(it.price * it.quantity)}</span>
              </div>
            ))}
          </div>
          <div className="space-y-1 mt-3 text-sm">
            <div className="flex justify-between"><span>Subtotal</span><span>{formatGBP(subtotal)}</span></div>
            <div className="flex justify-between"><span>Delivery</span><span data-testid="chk-delivery">{quote ? (quote.fee === 0 ? "Free" : formatGBP(quote.fee)) : "—"}</span></div>
            {quote && quote.away_from_free > 0 && <div className="text-xs text-afro-ink-soft">Add {formatGBP(quote.away_from_free)} more for free delivery.</div>}
          </div>
          <div className="flex justify-between font-semibold mt-3 pt-3 border-t border-afro-border">
            <span>Total</span>
            <span data-testid="chk-total">{formatGBP(subtotal + (quote?.fee || 0))}</span>
          </div>
          {err && <p className="text-sm text-afro-error mt-3">{err}</p>}
          <button type="submit" disabled={loading || (quote && !quote.available)} className="afr-btn-primary w-full mt-5 disabled:opacity-60" data-testid="pay-with-stripe-btn">
            {loading ? "Creating secure session…" : "Pay with Stripe"}
          </button>
          <p className="text-xs text-afro-ink-soft mt-3">Secured by Stripe · currency GBP (£)</p>
        </aside>
      </form>
    </div>
  );
}
