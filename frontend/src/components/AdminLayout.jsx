import React, { useState } from "react";
import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAdmin } from "../contexts";
import {
  LayoutDashboard, Package, FolderOpen, Layers, Utensils, Bot, Box, Tag,
  Warehouse, ShoppingBag, Users, Mail, FileText, BarChart3, UploadCloud,
  Settings, Shield, Truck, LogOut, Menu, X,
} from "lucide-react";

const NAV = [
  { to: "/admin/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/admin/products", icon: Package, label: "Products" },
  { to: "/admin/categories", icon: FolderOpen, label: "Categories" },
  { to: "/admin/collections", icon: Layers, label: "Collections" },
  { to: "/admin/meal-collections", icon: Utensils, label: "Meal Collections" },
  { to: "/admin/ai-mapping", icon: Bot, label: "AI Meal Mapping" },
  { to: "/admin/bundles", icon: Box, label: "Bundles & Upsells" },
  { to: "/admin/pricing", icon: Tag, label: "Pricing & Promotions" },
  { to: "/admin/inventory", icon: Warehouse, label: "Inventory" },
  { to: "/admin/orders", icon: ShoppingBag, label: "Orders" },
  { to: "/admin/customers", icon: Users, label: "Customers" },
  { to: "/admin/messaging", icon: Mail, label: "Messaging & Automations" },
  { to: "/admin/content", icon: FileText, label: "Content & Recipes" },
  { to: "/admin/analytics", icon: BarChart3, label: "Analytics & Reports" },
  { to: "/admin/imports", icon: UploadCloud, label: "Imports / Exports" },
  { to: "/admin/delivery", icon: Truck, label: "Delivery Zones" },
  { to: "/admin/audit", icon: Shield, label: "Audit Logs" },
  { to: "/admin/settings", icon: Settings, label: "Settings & Roles" },
];

export default function AdminLayout() {
  const { admin, logout } = useAdmin();
  const nav = useNavigate();
  const [open, setOpen] = useState(false);
  if (!admin) { nav("/admin/login"); return null; }
  return (
    <div className="admin-scope min-h-screen flex" data-testid="admin-layout">
      {/* Sidebar */}
      <aside className={`fixed lg:static inset-y-0 left-0 z-40 w-64 bg-[#111827] text-gray-300 transform ${open ? "translate-x-0" : "-translate-x-full"} lg:translate-x-0 transition-transform`}>
        <div className="h-16 flex items-center gap-2 px-5 border-b border-white/10">
          <div className="w-8 h-8 rounded bg-afro-primary flex items-center justify-center text-white font-display font-bold">A</div>
          <div>
            <div className="text-white font-semibold text-sm">Afrobean Admin</div>
            <div className="text-[10px] uppercase tracking-wider text-gray-500">{admin?.role?.replace("_", " ")}</div>
          </div>
        </div>
        <nav className="py-3 overflow-y-auto h-[calc(100vh-4rem-4rem)]">
          {NAV.map(n => (
            <NavLink key={n.to} to={n.to} onClick={() => setOpen(false)}
              className={({ isActive }) => `flex items-center gap-3 px-5 py-2 text-sm ${isActive ? "bg-white/10 text-white border-l-2 border-afro-accent" : "hover:bg-white/5 hover:text-white"}`}
              data-testid={`sidenav-${n.to.split("/").pop()}`}>
              <n.icon size={16} /> {n.label}
            </NavLink>
          ))}
        </nav>
        <div className="h-16 px-5 flex items-center border-t border-white/10">
          <button onClick={() => { logout(); nav("/admin/login"); }} className="flex items-center gap-2 text-sm hover:text-white" data-testid="admin-logout">
            <LogOut size={14} /> Sign out
          </button>
        </div>
      </aside>
      <div className="flex-1 min-w-0">
        <header className="h-16 bg-white border-b border-admin-border flex items-center px-6 gap-4">
          <button className="lg:hidden" onClick={() => setOpen(!open)}><Menu size={20} /></button>
          <div className="flex-1 font-admin text-sm text-gray-500">{admin?.email}</div>
          <a href="/" target="_blank" rel="noreferrer" className="text-xs text-gray-500 hover:text-gray-900" data-testid="view-storefront">View storefront ↗</a>
        </header>
        <main className="p-6 font-admin"><Outlet /></main>
      </div>
    </div>
  );
}
