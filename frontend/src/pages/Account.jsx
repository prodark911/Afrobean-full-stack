import React, { useEffect, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts";
import { api, formatGBP } from "../api";

export default function Account() {
  const { customer, loading, logout } = useAuth();
  const nav = useNavigate();
  const [tab, setTab] = useState("overview");
  const [orders, setOrders] = useState([]);
  const [wishlist, setWishlist] = useState({ products: [] });

  useEffect(() => {
    if (customer) {
      api.get("/orders").then(r => setOrders(r.data)).catch(() => {});
      api.get("/wishlist").then(r => setWishlist(r.data)).catch(() => {});
    }
  }, [customer]);

  if (loading) return <div className="p-16 text-center">Loading…</div>;
  if (!customer) return <Navigate to="/login" />;

  return (
    <div className="max-w-6xl mx-auto px-4 py-10" data-testid="account-page">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display text-4xl">Hi, {customer.name?.split(" ")[0]}</h1>
          <p className="text-afro-ink-soft mt-1">{customer.email}</p>
        </div>
        <button onClick={() => { logout(); nav("/"); }} className="afr-btn-outline" data-testid="logout-btn">Sign out</button>
      </div>
      <div className="flex gap-2 border-b border-afro-border mb-6">
        {[
          { k: "overview", l: "Overview" },
          { k: "orders", l: "Orders" },
          { k: "wishlist", l: "Wishlist" },
          { k: "details", l: "My details" },
        ].map(t => (
          <button key={t.k} onClick={() => setTab(t.k)} className={`py-3 px-4 text-sm font-medium ${tab === t.k ? "border-b-2 border-afro-primary text-afro-primary" : "text-afro-ink-soft"}`} data-testid={`tab-${t.k}`}>{t.l}</button>
        ))}
      </div>

      {tab === "overview" && (
        <div className="grid md:grid-cols-3 gap-4" data-testid="overview-tab">
          <div className="bg-white border border-afro-border rounded-xl p-5">
            <div className="text-xs uppercase tracking-widest text-afro-ink-soft">Orders</div>
            <div className="font-display text-3xl mt-1">{customer.order_count || 0}</div>
          </div>
          <div className="bg-white border border-afro-border rounded-xl p-5">
            <div className="text-xs uppercase tracking-widest text-afro-ink-soft">Total spend</div>
            <div className="font-display text-3xl mt-1">{formatGBP(customer.total_spend || 0)}</div>
          </div>
          <div className="bg-white border border-afro-border rounded-xl p-5">
            <div className="text-xs uppercase tracking-widest text-afro-ink-soft">Wishlist</div>
            <div className="font-display text-3xl mt-1">{wishlist.products?.length || 0}</div>
          </div>
        </div>
      )}

      {tab === "orders" && (
        <div className="bg-white border border-afro-border rounded-xl overflow-hidden" data-testid="orders-tab">
          {orders.length === 0 ? (
            <div className="p-8 text-center text-afro-ink-soft">No orders yet. <Link to="/shop" className="text-afro-primary">Start shopping →</Link></div>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-afro-surface-alt">
                <tr><th className="text-left p-3">Order</th><th className="text-left p-3">Status</th><th className="text-left p-3">Total</th><th className="text-left p-3">Date</th><th></th></tr>
              </thead>
              <tbody>
                {orders.map(o => (
                  <tr key={o.id} className="border-t border-afro-border" data-testid={`order-row-${o.order_number}`}>
                    <td className="p-3 font-mono">{o.order_number}</td>
                    <td className="p-3"><span className="capitalize">{o.status}</span></td>
                    <td className="p-3">{formatGBP(o.total)}</td>
                    <td className="p-3">{new Date(o.created_at).toLocaleDateString("en-GB")}</td>
                    <td className="p-3"><button onClick={() => api.post(`/orders/${o.order_number}/reorder`).then(() => alert("Added to basket"))} className="text-afro-primary text-xs font-semibold">Reorder</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {tab === "wishlist" && (
        <div data-testid="wishlist-tab">
          {wishlist.products?.length === 0 ? (
            <div className="p-8 text-center bg-white border border-afro-border rounded-xl text-afro-ink-soft">Your wishlist is empty.</div>
          ) : (
            <div className="grid md:grid-cols-3 lg:grid-cols-4 gap-4">
              {wishlist.products.map(p => (
                <Link key={p.id} to={`/p/${p.slug}`} className="bg-white border border-afro-border rounded-xl p-4">
                  {p.images?.[0] && <img src={p.images[0]} alt="" className="aspect-square object-cover rounded" />}
                  <div className="text-sm font-medium mt-2 line-clamp-2">{p.name}</div>
                  <div className="text-sm font-semibold mt-1">{formatGBP(p.price)}</div>
                </Link>
              ))}
            </div>
          )}
        </div>
      )}

      {tab === "details" && (
        <div className="bg-white border border-afro-border rounded-xl p-6 max-w-xl" data-testid="details-tab">
          <div className="space-y-3 text-sm">
            <div><b>Email:</b> {customer.email}</div>
            <div><b>Phone:</b> {customer.phone || "—"}</div>
            <div><b>Marketing consent:</b> {customer.marketing_consent ? "Yes" : "No"}</div>
            <div><b>WhatsApp consent:</b> {customer.whatsapp_consent ? "Yes" : "No"}</div>
          </div>
          <p className="text-xs text-afro-ink-soft mt-4">To update your details, contact support.</p>
        </div>
      )}
    </div>
  );
}
