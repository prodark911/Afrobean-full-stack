import React, { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, formatGBP } from "../api";
import { useCart } from "../contexts";
import { CheckCircle2 } from "lucide-react";

export default function CheckoutSuccess() {
  const [params] = useSearchParams();
  const sessionId = params.get("session_id");
  const orderNum = params.get("order");
  const [status, setStatus] = useState("pending");
  const [order, setOrder] = useState(null);
  const [attempts, setAttempts] = useState(0);
  const { refresh } = useCart();

  useEffect(() => {
    if (!sessionId) return;
    let t;
    const poll = async () => {
      try {
        const { data } = await api.get(`/checkout/status/${sessionId}`);
        setStatus(data.payment_status);
        if (data.payment_status === "paid") {
          refresh();
          if (orderNum) {
            try { const r = await api.get(`/orders/${orderNum}`); setOrder(r.data); } catch {}
          }
          return;
        }
        if (data.status === "expired") return;
        if (attempts < 12) { setAttempts(a => a + 1); t = setTimeout(poll, 2000); }
      } catch (e) { setStatus("error"); }
    };
    poll();
    return () => { if (t) clearTimeout(t); };
    // eslint-disable-next-line
  }, [sessionId]);

  return (
    <div className="max-w-3xl mx-auto px-4 py-20 text-center" data-testid="checkout-success-page">
      {status === "paid" ? (
        <>
          <CheckCircle2 size={72} className="text-afro-secondary mx-auto" />
          <h1 className="font-display text-4xl md:text-5xl mt-6">Payment successful!</h1>
          <p className="text-afro-ink-soft mt-3">Thank you for shopping with Afrobean. Your order is being packed.</p>
          {order && (
            <div className="bg-white border border-afro-border rounded-xl p-6 mt-8 text-left">
              <div className="text-xs uppercase tracking-widest text-afro-primary">Order</div>
              <div className="font-display text-2xl">{order.order_number}</div>
              <div className="mt-4 space-y-1 text-sm">
                <div className="flex justify-between"><span>Subtotal</span><span>{formatGBP(order.subtotal)}</span></div>
                <div className="flex justify-between"><span>Delivery</span><span>{order.delivery_fee === 0 ? "Free" : formatGBP(order.delivery_fee)}</span></div>
                <div className="flex justify-between font-semibold pt-1 border-t border-afro-border mt-1"><span>Total</span><span>{formatGBP(order.total)}</span></div>
              </div>
            </div>
          )}
          <div className="mt-8 flex gap-3 justify-center">
            <Link to="/account/orders" className="afr-btn-primary">View my orders</Link>
            <Link to="/shop" className="afr-btn-outline">Continue shopping</Link>
          </div>
        </>
      ) : status === "expired" || status === "error" ? (
        <>
          <h1 className="font-display text-3xl">Payment session expired</h1>
          <p className="mt-3 text-afro-ink-soft">Please try again.</p>
          <Link to="/cart" className="afr-btn-primary inline-block mt-6">Return to basket</Link>
        </>
      ) : (
        <>
          <div className="animate-pulse">
            <div className="w-16 h-16 rounded-full bg-afro-surface-alt mx-auto" />
            <h1 className="font-display text-3xl mt-6">Confirming your payment…</h1>
            <p className="mt-2 text-afro-ink-soft">Please hold on a few seconds.</p>
          </div>
        </>
      )}
    </div>
  );
}
