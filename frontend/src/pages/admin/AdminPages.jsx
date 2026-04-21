import React, { useEffect, useState } from "react";
import { Link, useParams, useNavigate, useSearchParams } from "react-router-dom";
import { api, formatGBP } from "../../api";
import { Search, Plus, Download, Upload, Edit3, Archive, Eye, CheckSquare, Square } from "lucide-react";

// -------------------- PRODUCTS --------------------
export function AdminProducts() {
  const [items, setItems] = useState([]); const [total, setTotal] = useState(0);
  const [q, setQ] = useState(""); const [status, setStatus] = useState("");
  const [selected, setSelected] = useState(new Set());
  const load = async () => {
    const { data } = await api.get("/admin/products", { params: { q, status, limit: 100 } });
    setItems(data.items); setTotal(data.total);
  };
  useEffect(() => { load(); }, [q, status]);

  const toggle = (id) => setSelected(s => { const n = new Set(s); n.has(id) ? n.delete(id) : n.add(id); return n; });
  const bulk = async (action) => {
    if (selected.size === 0) return;
    await api.post("/admin/products/bulk", { ids: [...selected], action });
    setSelected(new Set()); load();
  };
  const exportCsv = async () => {
    const token = localStorage.getItem("afr_admin_token");
    const r = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/exports/products`, { headers: { Authorization: `Bearer ${token}` } });
    const blob = await r.blob(); const url = URL.createObjectURL(blob);
    const a = document.createElement("a"); a.href = url; a.download = "afrobean-products.csv"; a.click();
  };

  return (
    <div data-testid="admin-products">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold">Products</h1>
          <p className="text-sm text-gray-500">{total} products in catalogue</p>
        </div>
        <div className="flex gap-2">
          <button onClick={exportCsv} className="px-3 py-2 text-sm border border-admin-border rounded flex items-center gap-2" data-testid="export-products"><Download size={14} /> Export</button>
          <Link to="/admin/imports" className="px-3 py-2 text-sm border border-admin-border rounded flex items-center gap-2"><Upload size={14} /> Import</Link>
          <Link to="/admin/products/new" className="bg-gray-900 text-white px-3 py-2 text-sm rounded flex items-center gap-2" data-testid="new-product"><Plus size={14} /> New product</Link>
        </div>
      </div>

      <div className="bg-white border border-admin-border rounded-lg mb-4 p-3 flex items-center gap-3">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input value={q} onChange={e => setQ(e.target.value)} placeholder="Search name or SKU..." className="afr-input pl-8" data-testid="product-search" />
        </div>
        <select value={status} onChange={e => setStatus(e.target.value)} className="afr-input max-w-[160px]" data-testid="product-status-filter">
          <option value="">All statuses</option>
          <option value="active">Active</option>
          <option value="draft">Draft</option>
          <option value="archived">Archived</option>
        </select>
      </div>

      {selected.size > 0 && (
        <div className="bg-gray-900 text-white rounded-lg p-3 mb-3 flex items-center gap-3" data-testid="bulk-toolbar">
          <span className="text-sm">{selected.size} selected</span>
          <button onClick={() => bulk("publish")} className="text-xs bg-white/10 px-3 py-1 rounded hover:bg-white/20">Publish</button>
          <button onClick={() => bulk("draft")} className="text-xs bg-white/10 px-3 py-1 rounded hover:bg-white/20">Move to draft</button>
          <button onClick={() => bulk("archive")} className="text-xs bg-white/10 px-3 py-1 rounded hover:bg-white/20">Archive</button>
          <button onClick={() => setSelected(new Set())} className="ml-auto text-xs opacity-70">Clear</button>
        </div>
      )}

      <div className="bg-white border border-admin-border rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50">
            <tr className="text-xs uppercase tracking-wider text-gray-500 text-left">
              <th className="p-3 w-10"></th>
              <th className="p-3">Product</th>
              <th className="p-3">SKU</th>
              <th className="p-3">Price</th>
              <th className="p-3">Stock</th>
              <th className="p-3">Status</th>
              <th className="p-3"></th>
            </tr>
          </thead>
          <tbody>
            {items.map(p => (
              <tr key={p.id} className="border-t border-admin-border hover:bg-gray-50" data-testid={`product-row-${p.slug}`}>
                <td className="p-3"><button onClick={() => toggle(p.id)}>{selected.has(p.id) ? <CheckSquare size={16} /> : <Square size={16} />}</button></td>
                <td className="p-3">
                  <div className="flex items-center gap-3">
                    {p.images?.[0] && <img src={p.images[0]} alt="" className="w-10 h-10 rounded object-cover" />}
                    <div><div className="font-medium">{p.name}</div><div className="text-xs text-gray-500">{p.brand}</div></div>
                  </div>
                </td>
                <td className="p-3 font-mono text-xs">{p.sku}</td>
                <td className="p-3">{formatGBP(p.price)}</td>
                <td className="p-3"><span className={p.stock < 10 ? "text-red-600 font-semibold" : ""}>{p.stock}</span></td>
                <td className="p-3"><Badge status={p.status} /></td>
                <td className="p-3"><Link to={`/admin/products/${p.id}`} className="text-xs text-afro-primary font-medium">Edit →</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function AdminProductEdit() {
  const { id } = useParams(); const nav = useNavigate();
  const [p, setP] = useState(null);
  const [cats, setCats] = useState([]);
  const isNew = id === "new";

  useEffect(() => {
    api.get("/admin/categories").then(r => setCats(r.data));
    if (!isNew) api.get(`/admin/products/${id}`).then(r => setP(r.data));
    else setP({ name: "", slug: "", brand: "Afrobean", description: "", price: 0, stock: 0, sku: "", category_id: "", images: [], status: "draft", variants: [], meal_tags: [], ai_meal_roles: [], featured: false, bestseller: false });
  }, [id]);

  if (!p) return <div className="text-sm text-gray-500">Loading…</div>;
  const save = async (e) => {
    e.preventDefault();
    if (isNew) { const { data } = await api.post("/admin/products", p); nav(`/admin/products/${data.id}`); }
    else { await api.patch(`/admin/products/${id}`, p); alert("Saved"); }
  };
  return (
    <form onSubmit={save} className="max-w-4xl" data-testid="product-edit-form">
      <Link to="/admin/products" className="text-sm text-gray-500">← Back to products</Link>
      <h1 className="text-2xl font-semibold mt-2 mb-6">{isNew ? "New product" : p.name}</h1>
      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <Section title="Basic details">
            <Field label="Name"><input required value={p.name} onChange={e => setP({ ...p, name: e.target.value })} className="afr-input" data-testid="pe-name" /></Field>
            <Field label="Slug"><input required value={p.slug} onChange={e => setP({ ...p, slug: e.target.value })} className="afr-input" data-testid="pe-slug" /></Field>
            <Field label="Brand"><input value={p.brand} onChange={e => setP({ ...p, brand: e.target.value })} className="afr-input" /></Field>
            <Field label="Description"><textarea rows={4} value={p.description} onChange={e => setP({ ...p, description: e.target.value })} className="afr-input" /></Field>
            <Field label="Category">
              <select value={p.category_id || ""} onChange={e => setP({ ...p, category_id: e.target.value })} className="afr-input">
                <option value="">—</option>
                {cats.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </Field>
            <Field label="Image URL"><input value={p.images?.[0] || ""} onChange={e => setP({ ...p, images: [e.target.value] })} className="afr-input" /></Field>
            <Field label="Meal tags (comma)"><input value={p.meal_tags?.join(",") || ""} onChange={e => setP({ ...p, meal_tags: e.target.value.split(",").map(x => x.trim()).filter(Boolean) })} className="afr-input" /></Field>
            <Field label="AI meal roles (comma)"><input value={p.ai_meal_roles?.join(",") || ""} onChange={e => setP({ ...p, ai_meal_roles: e.target.value.split(",").map(x => x.trim()).filter(Boolean) })} className="afr-input" /></Field>
          </Section>
          <Section title="Pricing & inventory">
            <div className="grid grid-cols-2 gap-3">
              <Field label="Price (£)"><input type="number" step="0.01" value={p.price} onChange={e => setP({ ...p, price: +e.target.value })} className="afr-input" data-testid="pe-price" /></Field>
              <Field label="Compare at"><input type="number" step="0.01" value={p.compare_at_price || ""} onChange={e => setP({ ...p, compare_at_price: +e.target.value || null })} className="afr-input" /></Field>
              <Field label="Cost"><input type="number" step="0.01" value={p.cost_price || ""} onChange={e => setP({ ...p, cost_price: +e.target.value || null })} className="afr-input" /></Field>
              <Field label="Stock"><input type="number" value={p.stock} onChange={e => setP({ ...p, stock: +e.target.value })} className="afr-input" data-testid="pe-stock" /></Field>
              <Field label="SKU"><input value={p.sku} onChange={e => setP({ ...p, sku: e.target.value })} className="afr-input" /></Field>
            </div>
          </Section>
        </div>
        <div className="space-y-4">
          <Section title="Status & visibility">
            <Field label="Status">
              <select value={p.status} onChange={e => setP({ ...p, status: e.target.value })} className="afr-input" data-testid="pe-status">
                <option value="draft">Draft</option><option value="active">Active</option><option value="archived">Archived</option>
              </select>
            </Field>
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={p.featured} onChange={e => setP({ ...p, featured: e.target.checked })} /> Featured</label>
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={p.bestseller} onChange={e => setP({ ...p, bestseller: e.target.checked })} /> Bestseller</label>
            <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={p.new_arrival || false} onChange={e => setP({ ...p, new_arrival: e.target.checked })} /> New arrival</label>
          </Section>
          <button type="submit" className="w-full bg-gray-900 text-white py-2 rounded-md text-sm font-medium hover:bg-gray-800" data-testid="pe-save">{isNew ? "Create product" : "Save changes"}</button>
        </div>
      </div>
    </form>
  );
}

function Section({ title, children }) {
  return <div className="bg-white border border-admin-border rounded-lg p-5"><h2 className="font-semibold mb-4 text-sm uppercase tracking-wide text-gray-500">{title}</h2><div className="space-y-3">{children}</div></div>;
}
function Field({ label, children }) { return <label className="block"><span className="text-xs text-gray-600">{label}</span>{children}</label>; }
function Badge({ status }) {
  const m = { active: "bg-emerald-100 text-emerald-800", draft: "bg-gray-100 text-gray-700", archived: "bg-red-100 text-red-800" };
  return <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full capitalize ${m[status]}`}>{status}</span>;
}


// -------------------- CATEGORIES / COLLECTIONS --------------------
export function AdminCategories() {
  const [items, setItems] = useState([]);
  const [edit, setEdit] = useState(null);
  const load = () => api.get("/admin/categories").then(r => setItems(r.data));
  useEffect(() => { load(); }, []);
  const save = async () => {
    if (edit.id) await api.patch(`/admin/categories/${edit.id}`, edit);
    else await api.post("/admin/categories", edit);
    setEdit(null); load();
  };
  return (
    <div data-testid="admin-categories">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold">Categories</h1>
        <button onClick={() => setEdit({ name: "", slug: "", description: "", image: "", sort_order: items.length, visible: true })} className="bg-gray-900 text-white px-3 py-2 text-sm rounded">+ New category</button>
      </div>
      <div className="bg-white border border-admin-border rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs uppercase tracking-wider text-gray-500 text-left">
            <tr><th className="p-3">Name</th><th>Slug</th><th>Products</th><th>Order</th><th>Visible</th><th></th></tr>
          </thead>
          <tbody>
            {items.map(c => (
              <tr key={c.id} className="border-t border-admin-border">
                <td className="p-3 font-medium">{c.name}</td>
                <td className="p-3 text-gray-500">{c.slug}</td>
                <td className="p-3">{c.product_count}</td>
                <td className="p-3">{c.sort_order}</td>
                <td className="p-3">{c.visible ? "Yes" : "No"}</td>
                <td className="p-3"><button onClick={() => setEdit({ ...c })} className="text-xs text-afro-primary">Edit</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {edit && (
        <Modal title={edit.id ? "Edit category" : "New category"} onClose={() => setEdit(null)}>
          <div className="space-y-3">
            <Field label="Name"><input value={edit.name} onChange={e => setEdit({ ...edit, name: e.target.value })} className="afr-input" /></Field>
            <Field label="Slug"><input value={edit.slug} onChange={e => setEdit({ ...edit, slug: e.target.value })} className="afr-input" /></Field>
            <Field label="Description"><textarea rows={2} value={edit.description} onChange={e => setEdit({ ...edit, description: e.target.value })} className="afr-input" /></Field>
            <Field label="Image URL"><input value={edit.image} onChange={e => setEdit({ ...edit, image: e.target.value })} className="afr-input" /></Field>
            <Field label="Sort order"><input type="number" value={edit.sort_order} onChange={e => setEdit({ ...edit, sort_order: +e.target.value })} className="afr-input" /></Field>
            <button onClick={save} className="bg-gray-900 text-white px-4 py-2 text-sm rounded">Save</button>
          </div>
        </Modal>
      )}
    </div>
  );
}

export function AdminCollections() {
  const [items, setItems] = useState([]);
  useEffect(() => { api.get("/admin/collections").then(r => setItems(r.data)); }, []);
  return (
    <div data-testid="admin-collections">
      <h1 className="text-2xl font-semibold mb-6">Collections</h1>
      <div className="grid md:grid-cols-3 gap-4">
        {items.map(c => (
          <div key={c.id} className="bg-white border border-admin-border rounded-lg p-4">
            <div className="text-xs uppercase tracking-wider text-gray-500">{c.type}</div>
            <div className="font-medium">{c.title}</div>
            <p className="text-xs text-gray-500 mt-1 line-clamp-2">{c.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}


// -------------------- ORDERS --------------------
export function AdminOrders() {
  const [items, setItems] = useState([]); const [q, setQ] = useState(""); const [status, setStatus] = useState("");
  const load = () => api.get("/admin/orders", { params: { q, status, limit: 100 } }).then(r => setItems(r.data.items));
  useEffect(() => { load(); }, [q, status]);
  return (
    <div data-testid="admin-orders">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold">Orders</h1>
      </div>
      <div className="bg-white border border-admin-border rounded-lg mb-4 p-3 flex gap-3">
        <input value={q} onChange={e => setQ(e.target.value)} placeholder="Search order number / email..." className="afr-input flex-1" data-testid="order-search" />
        <select value={status} onChange={e => setStatus(e.target.value)} className="afr-input max-w-[160px]">
          <option value="">All statuses</option>
          {["pending", "paid", "fulfilled", "shipped", "delivered", "cancelled"].map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>
      <div className="bg-white border border-admin-border rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs uppercase text-gray-500 text-left"><tr><th className="p-3">Order</th><th>Customer</th><th>Total</th><th>Status</th><th>Fulfillment</th><th>Date</th><th></th></tr></thead>
          <tbody>
            {items.map(o => (
              <tr key={o.id} className="border-t border-admin-border" data-testid={`admin-order-${o.order_number}`}>
                <td className="p-3 font-mono text-xs">{o.order_number}</td>
                <td className="p-3 text-xs">{o.customer_email || "Guest"}</td>
                <td className="p-3">{formatGBP(o.total)}</td>
                <td className="p-3 capitalize">{o.status}</td>
                <td className="p-3 capitalize text-xs text-gray-500">{o.fulfillment_status}</td>
                <td className="p-3 text-xs">{new Date(o.created_at).toLocaleDateString("en-GB")}</td>
                <td className="p-3"><Link to={`/admin/orders/${o.order_number}`} className="text-xs text-afro-primary">View →</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function AdminOrderDetail() {
  const { orderNumber } = useParams();
  const [o, setO] = useState(null);
  const load = () => api.get(`/admin/orders/${orderNumber}`).then(r => setO(r.data));
  useEffect(() => { load(); }, [orderNumber]);
  const setStatus = async (s) => { await api.patch(`/admin/orders/${orderNumber}`, { status: s }); load(); };
  const setFulfillment = async (s) => { await api.patch(`/admin/orders/${orderNumber}`, { fulfillment_status: s }); load(); };
  if (!o) return <div>Loading…</div>;
  return (
    <div data-testid="admin-order-detail">
      <Link to="/admin/orders" className="text-sm text-gray-500">← All orders</Link>
      <div className="flex items-center justify-between mt-2 mb-6">
        <div>
          <h1 className="text-2xl font-semibold">{o.order_number}</h1>
          <p className="text-sm text-gray-500">Placed {new Date(o.created_at).toLocaleString("en-GB")}</p>
        </div>
        <div className="flex gap-2">
          <select value={o.status} onChange={e => setStatus(e.target.value)} className="afr-input max-w-[180px]" data-testid="order-status-select">
            {["pending", "paid", "fulfilled", "shipped", "delivered", "cancelled"].map(s => <option key={s}>{s}</option>)}
          </select>
          <select value={o.fulfillment_status} onChange={e => setFulfillment(e.target.value)} className="afr-input max-w-[180px]">
            {["unfulfilled", "partial", "fulfilled"].map(s => <option key={s}>{s}</option>)}
          </select>
        </div>
      </div>
      <div className="grid lg:grid-cols-3 gap-4">
        <div className="bg-white border border-admin-border rounded-lg p-5 lg:col-span-2">
          <h2 className="font-semibold mb-3">Items</h2>
          {o.items.map(it => (
            <div key={it.product_id + it.variant_sku} className="flex justify-between border-b border-admin-border py-2 text-sm">
              <div>{it.name} × {it.quantity}</div><div>{formatGBP(it.price * it.quantity)}</div>
            </div>
          ))}
          <div className="mt-4 space-y-1 text-sm">
            <div className="flex justify-between"><span>Subtotal</span><span>{formatGBP(o.subtotal)}</span></div>
            <div className="flex justify-between"><span>Delivery</span><span>{o.delivery_fee === 0 ? "Free" : formatGBP(o.delivery_fee)}</span></div>
            <div className="flex justify-between font-semibold pt-2 border-t border-admin-border mt-2"><span>Total</span><span>{formatGBP(o.total)}</span></div>
          </div>
        </div>
        <div className="bg-white border border-admin-border rounded-lg p-5">
          <h2 className="font-semibold mb-3">Customer</h2>
          <div className="text-sm space-y-1">
            <div><b>Email:</b> {o.customer_email || "Guest"}</div>
            <div><b>Phone:</b> {o.address?.phone}</div>
            <div><b>Address:</b><br />{o.address?.line1}<br />{o.address?.city} {o.address?.postcode}<br />{o.address?.country}</div>
            <div><b>Payment:</b> <span className="capitalize">{o.payment_status}</span></div>
          </div>
          {o.notes && <><h3 className="font-semibold mt-4">Notes</h3><p className="text-sm text-gray-600">{o.notes}</p></>}
        </div>
        <div className="bg-white border border-admin-border rounded-lg p-5 lg:col-span-3">
          <h2 className="font-semibold mb-3">Timeline</h2>
          {(o.timeline || []).map((t, i) => (
            <div key={i} className="text-xs text-gray-600 py-1 border-b border-admin-border">
              <span className="font-mono">{new Date(t.at).toLocaleString("en-GB")}</span> — {t.by}: {JSON.stringify(t.change)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}


// -------------------- CUSTOMERS --------------------
export function AdminCustomers() {
  const [items, setItems] = useState([]); const [q, setQ] = useState("");
  useEffect(() => { api.get("/admin/customers", { params: { q, limit: 100 } }).then(r => setItems(r.data.items)); }, [q]);
  return (
    <div data-testid="admin-customers">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold">Customers</h1>
      </div>
      <div className="bg-white border border-admin-border rounded-lg mb-4 p-3">
        <input value={q} onChange={e => setQ(e.target.value)} placeholder="Search by email / name..." className="afr-input" />
      </div>
      <div className="bg-white border border-admin-border rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs uppercase text-gray-500 text-left"><tr><th className="p-3">Name</th><th>Email</th><th>Orders</th><th>Total spend</th><th>Consent</th><th>Joined</th></tr></thead>
          <tbody>
            {items.map(c => (
              <tr key={c.id} className="border-t border-admin-border">
                <td className="p-3 font-medium">{c.name}</td>
                <td className="p-3 text-gray-600">{c.email}</td>
                <td className="p-3">{c.order_count}</td>
                <td className="p-3">{formatGBP(c.total_spend)}</td>
                <td className="p-3 text-xs">{c.email_consent && "Email"}{c.whatsapp_consent && " · WhatsApp"}{c.marketing_consent && " · Marketing"}</td>
                <td className="p-3 text-xs text-gray-500">{new Date(c.created_at).toLocaleDateString("en-GB")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}


// -------------------- INVENTORY --------------------
export function AdminInventory() {
  const [params, setParams] = useSearchParams();
  const view = params.get("view") || "all";
  const [items, setItems] = useState([]);
  useEffect(() => { api.get("/admin/inventory", { params: { view } }).then(r => setItems(r.data)); }, [view]);
  const adjust = async (p) => {
    const delta = parseInt(prompt(`Adjust stock for ${p.name} by (+/-):`, "0") || "0");
    if (!delta) return;
    await api.post("/admin/inventory/adjust", { product_id: p.id, delta, reason: "admin adjust" });
    api.get("/admin/inventory", { params: { view } }).then(r => setItems(r.data));
  };
  return (
    <div data-testid="admin-inventory">
      <h1 className="text-2xl font-semibold mb-2">Inventory</h1>
      <div className="flex gap-2 mb-4 text-sm">
        {["all", "low_stock", "out_of_stock", "fast_movers", "dead_stock"].map(v => (
          <button key={v} onClick={() => setParams({ view: v })} className={`px-3 py-1 rounded-full border ${view === v ? "bg-gray-900 text-white border-gray-900" : "border-admin-border text-gray-600"}`} data-testid={`inv-filter-${v}`}>
            {v.replace("_", " ")}
          </button>
        ))}
      </div>
      <div className="bg-white border border-admin-border rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs uppercase text-gray-500 text-left"><tr><th className="p-3">Product</th><th>SKU</th><th>Stock</th><th>Threshold</th><th></th></tr></thead>
          <tbody>
            {items.map(p => (
              <tr key={p.id} className="border-t border-admin-border">
                <td className="p-3">{p.name}</td>
                <td className="p-3 font-mono text-xs">{p.sku}</td>
                <td className={`p-3 font-semibold ${p.stock === 0 ? "text-red-600" : p.stock < 10 ? "text-yellow-600" : ""}`}>{p.stock}</td>
                <td className="p-3 text-gray-500">{p.low_stock_threshold}</td>
                <td className="p-3"><button onClick={() => adjust(p)} className="text-xs text-afro-primary">Adjust</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}


// -------------------- AI MAPPING --------------------
export function AdminAIMapping() {
  const [items, setItems] = useState([]); const [active, setActive] = useState(null); const [prods, setProds] = useState([]);
  useEffect(() => {
    api.get("/admin/meal-collections").then(r => setItems(r.data));
    api.get("/admin/products").then(r => setProds(r.data.items));
  }, []);
  const load = (id) => api.get(`/admin/meal-collections/${id}`).then(r => setActive(r.data));
  const save = async () => {
    await api.patch(`/admin/meal-collections/${active.id}`, {
      required_slots: active.required_slots, optional_slots: active.optional_slots,
      user_intent_phrases: active.user_intent_phrases, title: active.title, description: active.description,
      tier: active.tier, servings_default: active.servings_default,
    });
    alert("Saved"); load(active.id);
  };
  const preview = async () => {
    const { data } = await api.post(`/admin/meal-collections/${active.id}/preview-basket`, {});
    alert(`Preview basket total: £${data.total.toFixed(2)}\n\n${data.basket.map(b => `${b.slot}: ${b.product.name}`).join("\n")}`);
  };
  const updateSlot = (groupKey, idx, patch) => {
    const next = { ...active };
    next[groupKey] = [...next[groupKey]];
    next[groupKey][idx] = { ...next[groupKey][idx], ...patch };
    setActive(next);
  };
  const prodName = (id) => prods.find(p => p.id === id)?.name || id;

  return (
    <div data-testid="admin-ai-mapping">
      <h1 className="text-2xl font-semibold mb-2">AI Meal Mapping</h1>
      <p className="text-sm text-gray-500 mb-6">Control what the Afrobean AI recommends for each meal.</p>
      <div className="grid lg:grid-cols-4 gap-4">
        <div className="bg-white border border-admin-border rounded-lg p-3">
          {items.map(m => (
            <button key={m.id} onClick={() => load(m.id)} className={`block text-left w-full px-3 py-2 rounded text-sm ${active?.id === m.id ? "bg-gray-900 text-white" : "hover:bg-gray-50"}`} data-testid={`ai-meal-${m.slug}`}>{m.title}</button>
          ))}
        </div>
        <div className="lg:col-span-3 bg-white border border-admin-border rounded-lg p-6 min-h-[400px]">
          {!active ? <div className="text-sm text-gray-500">Select a meal to edit its AI mapping →</div> : (
            <>
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h2 className="text-xl font-semibold">{active.title}</h2>
                  <div className="text-xs text-gray-500">{active.meal_tag}</div>
                </div>
                <div className="flex gap-2">
                  <button onClick={preview} className="text-xs px-3 py-2 border border-admin-border rounded" data-testid="ai-preview">Preview basket</button>
                  <button onClick={save} className="text-xs px-3 py-2 bg-gray-900 text-white rounded" data-testid="ai-save">Save</button>
                </div>
              </div>
              <Field label="Intent phrases (comma separated)">
                <input value={active.user_intent_phrases.join(", ")} onChange={e => setActive({ ...active, user_intent_phrases: e.target.value.split(",").map(s => s.trim()).filter(Boolean) })} className="afr-input" />
              </Field>
              <h3 className="font-semibold mt-5 mb-2">Required slots</h3>
              {active.required_slots.map((slot, idx) => (
                <SlotEditor key={slot.slot_key} slot={slot} prods={prods} prodName={prodName} onChange={p => updateSlot("required_slots", idx, p)} />
              ))}
              <h3 className="font-semibold mt-5 mb-2">Optional slots</h3>
              {active.optional_slots.map((slot, idx) => (
                <SlotEditor key={slot.slot_key} slot={slot} prods={prods} prodName={prodName} onChange={p => updateSlot("optional_slots", idx, p)} />
              ))}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function SlotEditor({ slot, prods, onChange, prodName }) {
  return (
    <div className="border border-admin-border rounded-md p-3 mb-2" data-testid={`slot-editor-${slot.slot_key}`}>
      <div className="flex items-center justify-between mb-2">
        <div><span className="font-mono text-xs text-gray-500">{slot.slot_key}</span> · <span className="text-sm font-medium">{slot.label}</span></div>
      </div>
      <div className="grid md:grid-cols-2 gap-2 text-xs">
        <div>
          <div className="text-gray-500 mb-1">Default picks</div>
          {slot.default_product_ids.map((pid, i) => (
            <div key={i} className="flex justify-between items-center bg-gray-50 px-2 py-1 rounded mb-1">
              <span className="truncate">{prodName(pid)}</span>
              <button onClick={() => onChange({ default_product_ids: slot.default_product_ids.filter(x => x !== pid) })} className="text-red-600">×</button>
            </div>
          ))}
          <select onChange={e => { if (e.target.value) { onChange({ default_product_ids: [...slot.default_product_ids, e.target.value] }); e.target.value = ""; } }} className="afr-input">
            <option value="">+ add default</option>{prods.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </div>
        <div>
          <div className="text-gray-500 mb-1">Substitutes</div>
          {slot.substitute_product_ids.map((pid, i) => (
            <div key={i} className="flex justify-between items-center bg-gray-50 px-2 py-1 rounded mb-1">
              <span className="truncate">{prodName(pid)}</span>
              <button onClick={() => onChange({ substitute_product_ids: slot.substitute_product_ids.filter(x => x !== pid) })} className="text-red-600">×</button>
            </div>
          ))}
          <select onChange={e => { if (e.target.value) { onChange({ substitute_product_ids: [...slot.substitute_product_ids, e.target.value] }); e.target.value = ""; } }} className="afr-input">
            <option value="">+ add substitute</option>{prods.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        </div>
      </div>
    </div>
  );
}


// -------------------- BUNDLES --------------------
export function AdminBundles() {
  const [items, setItems] = useState([]);
  useEffect(() => { api.get("/admin/bundles").then(r => setItems(r.data)); }, []);
  return (
    <div data-testid="admin-bundles">
      <h1 className="text-2xl font-semibold mb-6">Bundles & Upsells</h1>
      <div className="grid md:grid-cols-3 gap-4">
        {items.map(b => (
          <div key={b.id} className="bg-white border border-admin-border rounded-lg overflow-hidden">
            {b.image && <img src={b.image} alt="" className="aspect-video object-cover w-full" />}
            <div className="p-4">
              <div className="text-xs uppercase tracking-wider text-gray-500">{b.tier}</div>
              <div className="font-medium">{b.title}</div>
              <div className="mt-2 text-sm">{formatGBP(b.price)} <span className="text-gray-400 line-through ml-2">{formatGBP(b.compare_at_price)}</span></div>
              <div className="text-xs text-gray-500 mt-1">{b.items.length} items</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


// -------------------- MESSAGING --------------------
export function AdminMessaging() {
  const [tpls, setTpls] = useState([]); const [autos, setAutos] = useState([]);
  const load = async () => {
    setTpls((await api.get("/admin/messaging/templates")).data);
    setAutos((await api.get("/admin/messaging/automations")).data);
  };
  useEffect(() => { load(); }, []);
  const toggleAuto = async (a) => { await api.patch(`/admin/messaging/automations/${a.id}`, { active: !a.active }); load(); };
  return (
    <div data-testid="admin-messaging">
      <h1 className="text-2xl font-semibold mb-6">Messaging & Automations</h1>
      <div className="grid lg:grid-cols-2 gap-4">
        <div className="bg-white border border-admin-border rounded-lg p-5">
          <h2 className="font-semibold mb-4">Automations</h2>
          <div className="space-y-2">
            {autos.map(a => (
              <div key={a.id} className="flex items-center gap-3 p-3 border border-admin-border rounded" data-testid={`auto-${a.id}`}>
                <div className="flex-1">
                  <div className="font-medium text-sm">{a.name}</div>
                  <div className="text-xs text-gray-500 capitalize">{a.trigger.replace("_", " ")} · {a.channel} · delay {a.delay_minutes}m</div>
                </div>
                <button onClick={() => toggleAuto(a)} className={`text-xs px-3 py-1 rounded-full ${a.active ? "bg-emerald-100 text-emerald-800" : "bg-gray-100 text-gray-600"}`}>{a.active ? "Active" : "Inactive"}</button>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-white border border-admin-border rounded-lg p-5">
          <h2 className="font-semibold mb-4">Message templates</h2>
          <div className="space-y-2">
            {tpls.map(t => (
              <div key={t.id} className="p-3 border border-admin-border rounded text-sm">
                <div className="flex justify-between"><div className="font-medium">{t.name}</div><span className="text-[10px] uppercase text-gray-500">{t.channel}</span></div>
                {t.subject && <div className="text-xs text-gray-500 mt-1">Subject: {t.subject}</div>}
                <div className="text-xs text-gray-600 mt-1 line-clamp-2">{t.body}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}


// -------------------- ANALYTICS --------------------
export function AdminAnalytics() {
  const [d, setD] = useState(null);
  useEffect(() => { api.get("/admin/analytics/overview").then(r => setD(r.data)); }, []);
  if (!d) return <div>Loading…</div>;
  return (
    <div data-testid="admin-analytics">
      <h1 className="text-2xl font-semibold mb-6">Analytics & Reports</h1>
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-white border border-admin-border rounded-lg p-5"><div className="text-xs text-gray-500 uppercase">30d Revenue</div><div className="text-2xl font-semibold mt-2">{formatGBP(d.total_revenue_30d)}</div></div>
        <div className="bg-white border border-admin-border rounded-lg p-5"><div className="text-xs text-gray-500 uppercase">Orders (30d)</div><div className="text-2xl font-semibold mt-2">{d.order_count_30d}</div></div>
      </div>
      <div className="bg-white border border-admin-border rounded-lg p-5 mb-4">
        <h2 className="font-semibold mb-4">Sales by category</h2>
        {d.by_category.length === 0 ? <div className="text-sm text-gray-500">No paid orders yet.</div> :
          d.by_category.map(c => (
            <div key={c.name} className="mb-2">
              <div className="flex justify-between text-xs mb-1"><span>{c.name}</span><span>{formatGBP(c.value)}</span></div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden"><div className="h-full bg-afro-primary" style={{ width: `${Math.min(100, (c.value / (d.by_category[0]?.value || 1)) * 100)}%` }} /></div>
            </div>
          ))
        }
      </div>
      <div className="bg-white border border-admin-border rounded-lg p-5">
        <h2 className="font-semibold mb-4">Top products</h2>
        <table className="w-full text-sm">
          <thead><tr className="text-xs text-gray-500 text-left"><th className="py-2">Product</th><th>Price</th><th>Rating</th></tr></thead>
          <tbody>
            {d.top_products.map(p => (<tr key={p.slug} className="border-t border-admin-border"><td className="py-2">{p.name}</td><td>{formatGBP(p.price)}</td><td>★ {p.avg_rating?.toFixed?.(1)}</td></tr>))}
          </tbody>
        </table>
      </div>
    </div>
  );
}


// -------------------- IMPORTS --------------------
export function AdminImports() {
  const [log, setLog] = useState([]); const [result, setResult] = useState(null);
  useEffect(() => { api.get("/admin/imports").then(r => setLog(r.data)); }, []);
  const upload = async (e) => {
    e.preventDefault();
    const fd = new FormData(); fd.append("file", e.target.file.files[0]);
    const token = localStorage.getItem("afr_admin_token");
    const r = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/imports/products`, { method: "POST", body: fd, headers: { Authorization: `Bearer ${token}` } });
    setResult(await r.json()); api.get("/admin/imports").then(r => setLog(r.data));
  };
  return (
    <div data-testid="admin-imports">
      <h1 className="text-2xl font-semibold mb-6">Imports / Exports</h1>
      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-white border border-admin-border rounded-lg p-5">
          <h2 className="font-semibold mb-2">Import products (CSV)</h2>
          <p className="text-xs text-gray-500 mb-3">Headers: name, slug, brand, description, category_slug, price, sku, stock, tags, meal_tags, ai_meal_roles, image, status</p>
          <form onSubmit={upload}>
            <input type="file" accept=".csv" name="file" required className="mb-3 block" data-testid="import-file" />
            <button type="submit" className="bg-gray-900 text-white px-4 py-2 text-sm rounded">Upload</button>
          </form>
          {result && <pre className="bg-gray-50 p-3 mt-3 rounded text-xs max-h-48 overflow-auto">{JSON.stringify(result, null, 2)}</pre>}
        </div>
        <div className="bg-white border border-admin-border rounded-lg p-5">
          <h2 className="font-semibold mb-2">Recent imports</h2>
          <div className="space-y-2 text-xs">
            {log.map(i => (
              <div key={i.id} className="p-2 border border-admin-border rounded">
                <div className="flex justify-between"><b>{i.type}</b><span className="text-gray-500">{new Date(i.created_at).toLocaleString("en-GB")}</span></div>
                <div>Created: {i.created}, Errors: {i.errors?.length || 0}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}


// -------------------- OTHER SIMPLE PAGES --------------------
export function AdminAuditLogs() {
  const [items, setItems] = useState([]);
  useEffect(() => { api.get("/admin/audit-logs").then(r => setItems(r.data)); }, []);
  return (
    <div data-testid="admin-audit">
      <h1 className="text-2xl font-semibold mb-6">Audit Logs</h1>
      <div className="bg-white border border-admin-border rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs uppercase text-gray-500 text-left"><tr><th className="p-3">When</th><th>Actor</th><th>Action</th><th>Target</th></tr></thead>
          <tbody>
            {items.map(a => (
              <tr key={a.id} className="border-t border-admin-border">
                <td className="p-3 font-mono text-xs">{new Date(a.created_at).toLocaleString("en-GB")}</td>
                <td className="p-3 text-xs">{a.actor_email} <span className="text-gray-500">({a.actor_role})</span></td>
                <td className="p-3 font-mono text-xs">{a.action}</td>
                <td className="p-3 text-xs">{a.target_type} {a.target_id?.toString().slice(0, 10)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function AdminDelivery() {
  const [zones, setZones] = useState([]); const [edit, setEdit] = useState(null);
  const load = () => api.get("/admin/delivery-zones").then(r => setZones(r.data));
  useEffect(() => { load(); }, []);
  const save = async () => { await api.patch(`/admin/delivery-zones/${edit.id}`, edit); setEdit(null); load(); };
  return (
    <div data-testid="admin-delivery">
      <h1 className="text-2xl font-semibold mb-6">Delivery Zones</h1>
      {zones.map(z => (
        <div key={z.id} className="bg-white border border-admin-border rounded-lg p-5 mb-3">
          <div className="flex justify-between">
            <div>
              <div className="font-semibold">{z.name}</div>
              <div className="text-sm text-gray-500">{z.address}</div>
              <div className="text-xs text-gray-500 mt-1">Radius: {z.radius_miles} miles · Fee: £{z.per_mile_fee}/mile · Free over £{z.free_threshold}</div>
            </div>
            <button onClick={() => setEdit(z)} className="text-xs text-afro-primary">Edit</button>
          </div>
        </div>
      ))}
      {edit && (
        <Modal title="Edit delivery zone" onClose={() => setEdit(null)}>
          <Field label="Name"><input value={edit.name} onChange={e => setEdit({ ...edit, name: e.target.value })} className="afr-input" /></Field>
          <Field label="Address"><input value={edit.address} onChange={e => setEdit({ ...edit, address: e.target.value })} className="afr-input" /></Field>
          <Field label="Radius (miles)"><input type="number" step="0.1" value={edit.radius_miles} onChange={e => setEdit({ ...edit, radius_miles: +e.target.value })} className="afr-input" /></Field>
          <Field label="Per-mile fee (£)"><input type="number" step="0.01" value={edit.per_mile_fee} onChange={e => setEdit({ ...edit, per_mile_fee: +e.target.value })} className="afr-input" /></Field>
          <Field label="Free threshold (£)"><input type="number" step="0.01" value={edit.free_threshold} onChange={e => setEdit({ ...edit, free_threshold: +e.target.value })} className="afr-input" /></Field>
          <button onClick={save} className="bg-gray-900 text-white px-4 py-2 text-sm rounded mt-2">Save</button>
        </Modal>
      )}
    </div>
  );
}

export function AdminSettings() {
  const [users, setUsers] = useState([]); const [edit, setEdit] = useState(null);
  const load = () => api.get("/admin/admin-users").then(r => setUsers(r.data));
  useEffect(() => { load(); }, []);
  const create = async () => {
    await api.post("/admin/admin-users", edit); setEdit(null); load();
  };
  return (
    <div data-testid="admin-settings">
      <h1 className="text-2xl font-semibold mb-6">Settings & Roles</h1>
      <div className="bg-white border border-admin-border rounded-lg mb-4 overflow-hidden">
        <div className="p-4 flex items-center justify-between border-b border-admin-border">
          <h2 className="font-semibold">Team members</h2>
          <button onClick={() => setEdit({ email: "", name: "", role: "operations", password: "" })} className="text-xs bg-gray-900 text-white px-3 py-1.5 rounded">+ Add user</button>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs uppercase text-gray-500 text-left"><tr><th className="p-3">Name</th><th>Email</th><th>Role</th><th>Active</th></tr></thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id} className="border-t border-admin-border">
                <td className="p-3">{u.name}</td><td className="p-3">{u.email}</td><td className="p-3 capitalize">{u.role.replace("_", " ")}</td><td className="p-3">{u.active ? "Yes" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {edit && (
        <Modal title="New admin user" onClose={() => setEdit(null)}>
          <Field label="Name"><input value={edit.name} onChange={e => setEdit({ ...edit, name: e.target.value })} className="afr-input" /></Field>
          <Field label="Email"><input type="email" value={edit.email} onChange={e => setEdit({ ...edit, email: e.target.value })} className="afr-input" /></Field>
          <Field label="Role">
            <select value={edit.role} onChange={e => setEdit({ ...edit, role: e.target.value })} className="afr-input">
              {["super_admin", "merchandiser", "inventory_manager", "operations", "support", "marketing", "analyst"].map(r => <option key={r}>{r}</option>)}
            </select>
          </Field>
          <Field label="Password"><input type="password" value={edit.password} onChange={e => setEdit({ ...edit, password: e.target.value })} className="afr-input" /></Field>
          <button onClick={create} className="bg-gray-900 text-white px-4 py-2 text-sm rounded mt-2">Create</button>
        </Modal>
      )}
    </div>
  );
}

export function AdminContent() {
  return (
    <div data-testid="admin-content">
      <h1 className="text-2xl font-semibold mb-4">Content & Recipes</h1>
      <div className="bg-white border border-admin-border rounded-lg p-6 text-sm text-gray-500">
        Recipe pages and meal guides are connected to meal collections. Edit them via <Link to="/admin/meal-collections" className="text-afro-primary">Meal Collections</Link>.
      </div>
    </div>
  );
}

export function AdminPricing() {
  const [items, setItems] = useState([]);
  useEffect(() => { api.get("/admin/products", { params: { limit: 200 } }).then(r => setItems(r.data.items)); }, []);
  const margin = (p) => p.cost_price ? (((p.price - p.cost_price) / p.price) * 100).toFixed(0) + "%" : "—";
  return (
    <div data-testid="admin-pricing">
      <h1 className="text-2xl font-semibold mb-6">Pricing & Promotions</h1>
      <div className="bg-white border border-admin-border rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs uppercase text-gray-500 text-left"><tr><th className="p-3">Product</th><th>Price</th><th>Compare at</th><th>Cost</th><th>Margin</th></tr></thead>
          <tbody>
            {items.map(p => (
              <tr key={p.id} className="border-t border-admin-border">
                <td className="p-3">{p.name}</td>
                <td className="p-3">{formatGBP(p.price)}</td>
                <td className="p-3">{p.compare_at_price ? formatGBP(p.compare_at_price) : "—"}</td>
                <td className="p-3">{p.cost_price ? formatGBP(p.cost_price) : <span className="text-red-600 text-xs">missing</span>}</td>
                <td className="p-3 font-mono text-xs">{margin(p)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function AdminMealCollections() {
  const [items, setItems] = useState([]);
  useEffect(() => { api.get("/admin/meal-collections").then(r => setItems(r.data)); }, []);
  return (
    <div data-testid="admin-meal-collections">
      <h1 className="text-2xl font-semibold mb-6">Meal Collections</h1>
      <div className="grid md:grid-cols-3 gap-4">
        {items.map(m => (
          <Link key={m.id} to="/admin/ai-mapping" className="bg-white border border-admin-border rounded-lg overflow-hidden hover:shadow">
            {m.hero_image && <img src={m.hero_image} className="aspect-video object-cover w-full" alt="" />}
            <div className="p-4">
              <div className="text-xs uppercase tracking-wider text-gray-500">{m.meal_tag}</div>
              <div className="font-medium">{m.title}</div>
              <div className="text-xs text-gray-500 mt-1">{m.required_slots.length} required · {m.optional_slots.length} optional</div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}


function Modal({ title, onClose, children }) {
  return (
    <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg max-w-lg w-full p-6 font-admin">
        <div className="flex justify-between items-center mb-4"><h3 className="font-semibold">{title}</h3><button onClick={onClose}>×</button></div>
        {children}
      </div>
    </div>
  );
}
