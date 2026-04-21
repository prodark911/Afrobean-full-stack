import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, formatGBP } from "../../api";
import { TrendingUp, ShoppingBag, Users, Package, AlertTriangle, Sparkles } from "lucide-react";

function Stat({ label, value, icon: Icon, testId }) {
  return (
    <div className="bg-white border border-admin-border rounded-lg p-5" data-testid={testId}>
      <div className="flex items-center justify-between">
        <span className="text-xs uppercase tracking-wider text-gray-500">{label}</span>
        {Icon && <Icon size={16} className="text-gray-400" />}
      </div>
      <div className="text-2xl font-semibold mt-2 text-gray-900">{value}</div>
    </div>
  );
}

export default function Dashboard() {
  const [d, setD] = useState(null);
  useEffect(() => { api.get("/admin/dashboard").then(r => setD(r.data)); }, []);
  if (!d) return <div className="p-8 text-sm text-gray-500">Loading dashboard…</div>;
  return (
    <div data-testid="admin-dashboard">
      <h1 className="text-2xl font-semibold text-gray-900 mb-1">Dashboard</h1>
      <p className="text-sm text-gray-500 mb-6">A real-time snapshot of Afrobean's operations.</p>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Stat label="Today's sales" value={formatGBP(d.sales.today)} icon={TrendingUp} testId="kpi-today" />
        <Stat label="Weekly sales" value={formatGBP(d.sales.week)} icon={TrendingUp} testId="kpi-week" />
        <Stat label="Monthly sales" value={formatGBP(d.sales.month)} icon={TrendingUp} testId="kpi-month" />
        <Stat label="Avg order value" value={formatGBP(d.aov)} icon={ShoppingBag} testId="kpi-aov" />
      </div>
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Stat label="Repeat purchase rate" value={`${d.repeat_purchase_rate}%`} icon={Users} testId="kpi-repeat" />
        <Stat label="Total products" value={d.totals.products} icon={Package} testId="kpi-products" />
        <Stat label="Total customers" value={d.totals.customers} icon={Users} testId="kpi-customers" />
        <Stat label="AI sessions today" value={d.ai_sessions_today} icon={Sparkles} testId="kpi-ai" />
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="bg-white border border-admin-border rounded-lg p-5 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold">Recent orders</h2>
            <Link to="/admin/orders" className="text-xs text-afro-primary">View all →</Link>
          </div>
          <table className="w-full text-sm">
            <thead><tr className="text-xs text-gray-500 text-left border-b border-admin-border"><th className="py-2">Order</th><th>Customer</th><th>Total</th><th>Status</th></tr></thead>
            <tbody>
              {d.recent_orders.map(o => (
                <tr key={o.id} className="border-b border-admin-border" data-testid={`recent-order-${o.order_number}`}>
                  <td className="py-2 font-mono text-xs">{o.order_number}</td>
                  <td className="text-xs">{o.customer_email || "Guest"}</td>
                  <td className="text-xs">{formatGBP(o.total)}</td>
                  <td><Badge status={o.status} /></td>
                </tr>
              ))}
              {d.recent_orders.length === 0 && <tr><td colSpan={4} className="py-6 text-center text-gray-400">No orders yet</td></tr>}
            </tbody>
          </table>
        </div>

        <div className="bg-white border border-admin-border rounded-lg p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold">Orders by status</h2>
          </div>
          <div className="space-y-2 text-sm">
            {Object.entries(d.orders_by_status).map(([k, v]) => (
              <div key={k} className="flex justify-between"><span className="capitalize text-gray-600">{k}</span><span className="font-semibold">{v}</span></div>
            ))}
          </div>
        </div>

        <div className="bg-white border border-admin-border rounded-lg p-5 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold flex items-center gap-2"><AlertTriangle size={14} className="text-yellow-600" /> Low stock</h2>
            <Link to="/admin/inventory?view=low_stock" className="text-xs text-afro-primary">Inventory →</Link>
          </div>
          <table className="w-full text-sm">
            <thead><tr className="text-xs text-gray-500 text-left border-b border-admin-border"><th className="py-2">Product</th><th>Stock</th><th>SKU</th></tr></thead>
            <tbody>
              {d.low_stock_products.map(p => (
                <tr key={p.id} className="border-b border-admin-border" data-testid={`low-stock-${p.id}`}>
                  <td className="py-2 text-xs">{p.name}</td>
                  <td className="text-xs text-red-600 font-semibold">{p.stock}</td>
                  <td className="text-xs text-gray-500">{p.sku}</td>
                </tr>
              ))}
              {d.low_stock_products.length === 0 && <tr><td colSpan={3} className="py-6 text-center text-gray-400">All good — no low stock</td></tr>}
            </tbody>
          </table>
        </div>

        <div className="bg-white border border-admin-border rounded-lg p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold">Top products</h2>
          </div>
          <div className="space-y-3">
            {d.top_products.slice(0, 6).map(p => (
              <div key={p.id} className="flex items-center gap-3">
                {p.images?.[0] && <img src={p.images[0]} className="w-10 h-10 rounded object-cover" alt="" />}
                <div className="flex-1 min-w-0 text-xs">
                  <div className="font-medium truncate">{p.name}</div>
                  <div className="text-gray-500">{formatGBP(p.price)} · ★ {p.avg_rating?.toFixed?.(1)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white border border-admin-border rounded-lg p-5 lg:col-span-3">
          <h2 className="font-semibold mb-4">Meal collection performance</h2>
          <div className="grid md:grid-cols-3 gap-4">
            {d.meal_performance.map(m => (
              <div key={m.slug} className="p-4 border border-admin-border rounded-md">
                <div className="text-xs uppercase tracking-widest text-gray-500">{m.meal_tag}</div>
                <div className="font-medium">{m.title}</div>
                <div className="text-xs text-gray-500 mt-1">{m.orders_linked} orders this month</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function Badge({ status }) {
  const map = {
    pending: "bg-yellow-100 text-yellow-800", paid: "bg-emerald-100 text-emerald-800",
    fulfilled: "bg-blue-100 text-blue-800", shipped: "bg-indigo-100 text-indigo-800",
    delivered: "bg-green-100 text-green-800", cancelled: "bg-gray-100 text-gray-800",
  };
  return <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full capitalize ${map[status] || "bg-gray-100 text-gray-800"}`}>{status}</span>;
}
