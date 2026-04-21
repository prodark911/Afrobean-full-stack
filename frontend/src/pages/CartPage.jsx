import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useCart } from "../contexts";
import { formatGBP } from "../api";
import { Minus, Plus, Trash2 } from "lucide-react";

export default function CartPage() {
  const { cart, update, remove } = useCart();
  const nav = useNavigate();
  const subtotal = cart.items?.reduce((a, b) => a + b.price * b.quantity, 0) || 0;
  const away = Math.max(0, 50 - subtotal);
  const progress = Math.min(100, (subtotal / 50) * 100);
  if (!cart.items || cart.items.length === 0) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-20 text-center" data-testid="cart-empty-page">
        <i className="fa-solid fa-basket-shopping text-6xl text-afro-border mb-6" />
        <h1 className="font-display text-4xl">Your basket is empty.</h1>
        <p className="text-afro-ink-soft mt-3">Start with a meal collection or ask Afrobean AI what to cook.</p>
        <div className="mt-8 flex flex-col sm:flex-row gap-3 justify-center">
          <Link to="/meal-collections" className="afr-btn-primary">Browse meal collections</Link>
          <Link to="/ai-assistant" className="afr-btn-outline">Ask Afrobean AI</Link>
        </div>
      </div>
    );
  }
  return (
    <div className="max-w-7xl mx-auto px-4 py-10" data-testid="cart-page">
      <h1 className="font-display text-4xl md:text-5xl mb-2">Your basket</h1>
      <p className="text-afro-ink-soft mb-8">{cart.items.length} items</p>
      <div className="grid lg:grid-cols-3 gap-10">
        <div className="lg:col-span-2">
          <div className="bg-afro-surface-alt rounded-xl p-4 mb-6">
            {away > 0 ? (
              <>
                <p className="text-sm text-afro-ink-soft mb-2">You're <span className="font-semibold text-afro-primary">{formatGBP(away)}</span> away from free delivery.</p>
                <div className="h-2 rounded-full bg-afro-border overflow-hidden"><div className="h-full bg-afro-primary transition-all" style={{ width: `${progress}%` }} /></div>
              </>
            ) : (
              <p className="text-sm font-medium text-afro-secondary">🎉 You've unlocked free delivery!</p>
            )}
          </div>
          <div className="bg-white border border-afro-border rounded-xl divide-y divide-afro-border">
            {cart.items.map(it => (
              <div key={`${it.product_id}-${it.variant_sku}`} className="p-4 flex gap-4" data-testid={`cart-row-${it.product_id}`}>
                {it.image && <img src={it.image} alt="" className="w-24 h-24 rounded-md object-cover" />}
                <div className="flex-1">
                  <div className="font-medium">{it.name}</div>
                  {it.size_label && <div className="text-xs text-afro-ink-soft">{it.size_label}</div>}
                  <div className="text-sm font-semibold mt-1">{formatGBP(it.price)}</div>
                  <div className="flex items-center gap-2 mt-3">
                    <button className="w-8 h-8 border border-afro-border rounded flex items-center justify-center" onClick={() => update(it.product_id, it.variant_sku, Math.max(1, it.quantity - 1))}><Minus size={14} /></button>
                    <span className="w-8 text-center">{it.quantity}</span>
                    <button className="w-8 h-8 border border-afro-border rounded flex items-center justify-center" onClick={() => update(it.product_id, it.variant_sku, it.quantity + 1)}><Plus size={14} /></button>
                    <button onClick={() => remove(it.product_id, it.variant_sku)} className="ml-auto text-afro-ink-soft hover:text-afro-error"><Trash2 size={16} /></button>
                  </div>
                </div>
                <div className="text-right font-semibold">{formatGBP(it.price * it.quantity)}</div>
              </div>
            ))}
          </div>
        </div>
        <aside className="bg-white border border-afro-border rounded-xl p-6 h-fit lg:sticky lg:top-28" data-testid="cart-summary">
          <h3 className="font-display text-2xl mb-4">Order summary</h3>
          <div className="flex justify-between text-sm py-1"><span>Subtotal</span><span data-testid="cart-page-subtotal">{formatGBP(subtotal)}</span></div>
          <div className="flex justify-between text-sm py-1 text-afro-ink-soft"><span>Delivery</span><span>Calculated at checkout</span></div>
          <div className="border-t border-afro-border mt-3 pt-3 flex justify-between font-semibold">
            <span>Total</span><span>{formatGBP(subtotal)}</span>
          </div>
          <button onClick={() => nav("/checkout")} className="afr-btn-primary w-full mt-6" data-testid="cart-checkout-btn">Proceed to checkout</button>
          <Link to="/shop" className="block mt-3 text-center text-sm text-afro-primary hover:underline">Continue shopping</Link>
        </aside>
      </div>
    </div>
  );
}
