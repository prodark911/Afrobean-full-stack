import React, { useEffect, useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth, useCart } from "../contexts";
import { api, formatGBP } from "../api";
import { Search, ShoppingBag, User, Menu, X, Sparkles, MessageCircle } from "lucide-react";

export function AnnouncementBar() {
  return (
    <div className="announcement-bar text-white text-xs sm:text-sm" data-testid="announcement-bar">
      <div className="max-w-7xl mx-auto px-4 py-2 flex items-center justify-center gap-3 text-center tracking-wide">
        <i className="fa-solid fa-truck-fast" aria-hidden />
        <span>Free delivery on orders over £50 · Peterborough only (within 5 miles)</span>
      </div>
    </div>
  );
}

export function SecondaryBar() {
  return (
    <div className="bg-afro-surface-alt text-afro-ink-soft text-xs">
      <div className="max-w-7xl mx-auto px-4 py-2 flex flex-wrap items-center justify-between gap-2">
        <span className="font-medium tracking-wide uppercase">Peterborough's premium African food supermarket</span>
        <span className="hidden md:inline">Fresh groceries · Pantry staples · Frozen foods · Beauty · Smart meal-to-cart shopping</span>
      </div>
    </div>
  );
}

export default function StorefrontHeader() {
  const { customer, logout } = useAuth();
  const { count, setDrawerOpen } = useCart();
  const [q, setQ] = useState("");
  const [mobileOpen, setMobileOpen] = useState(false);
  const nav = useNavigate();
  const [categories, setCategories] = useState([]);
  useEffect(() => { api.get("/categories").then(r => setCategories(r.data)).catch(() => {}); }, []);

  const onSearch = (e) => {
    e.preventDefault();
    if (q.trim()) nav(`/search?q=${encodeURIComponent(q.trim())}`);
  };

  return (
    <header className="sticky top-0 z-40 bg-afro-bg border-b border-afro-border">
      <AnnouncementBar />
      <SecondaryBar />
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-4">
        <button className="md:hidden text-afro-ink" onClick={() => setMobileOpen(true)} data-testid="mobile-menu-btn">
          <Menu size={22} />
        </button>
        <Link to="/" className="flex items-center gap-2" data-testid="logo-link">
          <div className="w-9 h-9 rounded-lg bg-afro-primary flex items-center justify-center text-afro-bg font-display font-bold text-xl">A</div>
          <div className="leading-none">
            <div className="font-display text-2xl font-semibold text-afro-ink">Afrobean</div>
            <div className="text-[10px] tracking-[0.2em] uppercase text-afro-ink-soft">Peterborough · UK</div>
          </div>
        </Link>
        <form onSubmit={onSearch} className="flex-1 hidden md:flex max-w-2xl mx-6 relative" data-testid="search-form">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-afro-ink-soft" size={18} />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search for rice, palm oil, pepper soup spice, frozen fish..."
            className="afr-input pl-10"
            data-testid="search-input"
          />
        </form>
        <Link to="/ai-assistant" className="hidden lg:flex items-center gap-1 text-sm font-medium text-afro-primary hover:text-afro-primary-hover" data-testid="ai-cta-header">
          <Sparkles size={16} /> Ask AI
        </Link>
        {customer ? (
          <Link to="/account" className="hidden md:flex items-center gap-2 text-sm text-afro-ink" data-testid="account-link">
            <User size={18} /> <span className="hidden lg:inline">{customer.name?.split(" ")[0]}</span>
          </Link>
        ) : (
          <Link to="/login" className="hidden md:flex items-center gap-2 text-sm text-afro-ink" data-testid="login-link">
            <User size={18} /> <span className="hidden lg:inline">Sign in</span>
          </Link>
        )}
        <button onClick={() => setDrawerOpen(true)} className="relative flex items-center gap-2 text-afro-ink" data-testid="cart-btn">
          <ShoppingBag size={22} />
          {count > 0 && <span className="absolute -top-2 -right-2 bg-afro-primary text-white text-[10px] font-bold rounded-full w-5 h-5 flex items-center justify-center" data-testid="cart-count">{count}</span>}
        </button>
      </div>

      {/* Category nav */}
      <nav className="hidden md:block border-t border-afro-border">
        <div className="max-w-7xl mx-auto px-4 py-2 flex items-center gap-6 overflow-x-auto text-sm">
          <NavLink to="/shop" className={({ isActive }) => `whitespace-nowrap font-medium ${isActive ? "text-afro-primary" : "text-afro-ink hover:text-afro-primary"}`} data-testid="nav-shop-all">Shop All</NavLink>
          {categories.slice(0, 8).map(c => (
            <NavLink key={c.slug} to={`/category/${c.slug}`} className={({ isActive }) => `whitespace-nowrap ${isActive ? "text-afro-primary" : "text-afro-ink-soft hover:text-afro-primary"}`} data-testid={`nav-cat-${c.slug}`}>
              {c.name}
            </NavLink>
          ))}
          <NavLink to="/meal-collections" className="whitespace-nowrap text-afro-ink-soft hover:text-afro-primary" data-testid="nav-meal-collections">Meal Collections</NavLink>
          <NavLink to="/collection/best-sellers" className="whitespace-nowrap text-afro-ink-soft hover:text-afro-primary" data-testid="nav-bestsellers">Best Sellers</NavLink>
          <NavLink to="/collection/new-arrivals" className="whitespace-nowrap text-afro-ink-soft hover:text-afro-primary" data-testid="nav-new-arrivals">New Arrivals</NavLink>
        </div>
      </nav>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 bg-afro-bg" data-testid="mobile-menu">
          <div className="flex items-center justify-between p-4 border-b border-afro-border">
            <span className="font-display text-2xl">Menu</span>
            <button onClick={() => setMobileOpen(false)}><X /></button>
          </div>
          <form onSubmit={onSearch} className="p-4">
            <input value={q} onChange={e => setQ(e.target.value)} placeholder="Search..." className="afr-input" data-testid="mobile-search-input" />
          </form>
          <div className="flex flex-col">
            <Link to="/shop" onClick={() => setMobileOpen(false)} className="px-4 py-3 border-b border-afro-border">Shop All</Link>
            <Link to="/meal-collections" onClick={() => setMobileOpen(false)} className="px-4 py-3 border-b border-afro-border">Meal Collections</Link>
            <Link to="/ai-assistant" onClick={() => setMobileOpen(false)} className="px-4 py-3 border-b border-afro-border text-afro-primary font-medium">Ask Afrobean AI</Link>
            {categories.map(c => (
              <Link key={c.slug} to={`/category/${c.slug}`} onClick={() => setMobileOpen(false)} className="px-4 py-3 border-b border-afro-border">{c.name}</Link>
            ))}
            {customer ? (
              <>
                <Link to="/account" onClick={() => setMobileOpen(false)} className="px-4 py-3 border-b border-afro-border">My Account</Link>
                <button onClick={() => { logout(); setMobileOpen(false); }} className="text-left px-4 py-3 border-b border-afro-border">Sign out</button>
              </>
            ) : (
              <Link to="/login" onClick={() => setMobileOpen(false)} className="px-4 py-3 border-b border-afro-border">Sign in</Link>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
