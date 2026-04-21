import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { X, Minus, Plus, Trash2 } from "lucide-react";
import { useCart } from "../contexts";
import { formatGBP } from "../api";

export default function CartDrawer() {
  const { cart, drawerOpen, setDrawerOpen, update, remove } = useCart();
  const nav = useNavigate();
  const subtotal = cart.items?.reduce((a, b) => a + b.price * b.quantity, 0) || 0;
  const away = Math.max(0, 50 - subtotal);
  const progress = Math.min(100, (subtotal / 50) * 100);
  if (!drawerOpen) return null;
  return (
    <div className="fixed inset-0 z-50" data-testid="cart-drawer">
      <div className="absolute inset-0 bg-black/40" onClick={() => setDrawerOpen(false)} />
      <div className="absolute right-0 top-0 bottom-0 w-full sm:w-[420px] bg-afro-bg flex flex-col animate-slide-in">
        <div className="flex items-center justify-between p-5 border-b border-afro-border">
          <h3 className="font-display text-2xl">Your Basket</h3>
          <button onClick={() => setDrawerOpen(false)} data-testid="cart-close"><X /></button>
        </div>
        {(!cart.items || cart.items.length === 0) ? (
          <div className="flex-1 flex flex-col items-center justify-center p-8 text-center" data-testid="cart-empty">
            <i className="fa-solid fa-basket-shopping text-5xl text-afro-border mb-4" />
            <p className="text-afro-ink font-medium mb-2">Your basket is empty.</p>
            <p className="text-sm text-afro-ink-soft mb-6">Start with a meal collection or ask Afrobean AI what to cook.</p>
            <div className="flex flex-col gap-2 w-full">
              <button onClick={() => { setDrawerOpen(false); nav("/meal-collections"); }} className="afr-btn-primary" data-testid="cart-browse-meals">Browse Meal Collections</button>
              <button onClick={() => { setDrawerOpen(false); nav("/ai-assistant"); }} className="afr-btn-outline" data-testid="cart-ask-ai">Ask Afrobean AI</button>
            </div>
          </div>
        ) : (
          <>
            <div className="px-5 py-3 bg-afro-surface-alt border-b border-afro-border">
              {away > 0 ? (
                <>
                  <p className="text-xs text-afro-ink-soft mb-2">You're <span className="font-semibold text-afro-primary">{formatGBP(away)}</span> away from free delivery.</p>
                  <div className="h-1.5 rounded-full bg-afro-border overflow-hidden"><div className="h-full bg-afro-primary transition-all" style={{ width: `${progress}%` }} /></div>
                </>
              ) : (
                <p className="text-sm font-medium text-afro-secondary">🎉 You've unlocked free delivery!</p>
              )}
            </div>
            <div className="flex-1 overflow-y-auto">
              {cart.items.map((it) => (
                <div key={`${it.product_id}-${it.variant_sku}`} className="flex gap-3 p-4 border-b border-afro-border" data-testid={`cart-item-${it.product_id}`}>
                  {it.image && <img src={it.image} alt="" className="w-20 h-20 rounded-md object-cover" />}
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm leading-snug line-clamp-2">{it.name}</div>
                    {it.size_label && <div className="text-xs text-afro-ink-soft">{it.size_label}</div>}
                    <div className="text-sm font-semibold mt-1">{formatGBP(it.price)}</div>
                    <div className="flex items-center gap-2 mt-2">
                      <button className="w-7 h-7 flex items-center justify-center border border-afro-border rounded" onClick={() => update(it.product_id, it.variant_sku, Math.max(1, it.quantity - 1))}><Minus size={14} /></button>
                      <span className="text-sm min-w-[20px] text-center" data-testid={`qty-${it.product_id}`}>{it.quantity}</span>
                      <button className="w-7 h-7 flex items-center justify-center border border-afro-border rounded" onClick={() => update(it.product_id, it.variant_sku, it.quantity + 1)}><Plus size={14} /></button>
                      <button onClick={() => remove(it.product_id, it.variant_sku)} className="ml-auto text-afro-ink-soft hover:text-afro-error" data-testid={`remove-${it.product_id}`}><Trash2 size={16} /></button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <div className="p-5 border-t border-afro-border space-y-3 bg-white">
              <div className="flex justify-between text-sm"><span>Subtotal</span><span className="font-semibold" data-testid="cart-subtotal">{formatGBP(subtotal)}</span></div>
              <div className="flex justify-between text-xs text-afro-ink-soft"><span>Delivery calculated at checkout</span></div>
              <button onClick={() => { setDrawerOpen(false); nav("/cart"); }} className="afr-btn-outline w-full" data-testid="view-cart-btn">View full basket</button>
              <button onClick={() => { setDrawerOpen(false); nav("/checkout"); }} className="afr-btn-primary w-full" data-testid="checkout-btn">Checkout</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
