import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api, formatGBP } from "../api";
import { useCart, useAuth } from "../contexts";
import ProductCard from "../components/ProductCard";
import { Heart, ShoppingBag, Star, Truck, Shield, RefreshCw } from "lucide-react";

export default function PDP() {
  const { slug } = useParams();
  const { add } = useCart();
  const { customer } = useAuth();
  const [data, setData] = useState(null);
  const [variant, setVariant] = useState(null);
  const [qty, setQty] = useState(1);
  const [wish, setWish] = useState(false);
  const [activeImg, setActiveImg] = useState(0);

  useEffect(() => {
    api.get(`/products/${slug}`).then(r => {
      setData(r.data);
      const def = r.data.product.variants.find(v => v.is_default) || r.data.product.variants[0];
      setVariant(def);
    });
    if (customer) api.get("/wishlist").then(r => setWish(r.data.product_ids.includes(data?.product?.id))).catch(() => {});
  }, [slug, customer]);

  if (!data) return <div className="p-16 text-center">Loading...</div>;
  const p = data.product;
  const price = variant?.price || p.price;
  const compareAt = variant?.compare_at_price || p.compare_at_price;

  const toggleWish = async () => {
    if (!customer) return window.location.href = "/login";
    const res = await api.post("/wishlist/toggle", { product_id: p.id });
    setWish(res.data.product_ids.includes(p.id));
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-10" data-testid="pdp-page">
      <div className="text-sm text-afro-ink-soft mb-6">
        {data.category && <Link to={`/category/${data.category.slug}`} className="hover:text-afro-primary">{data.category.name}</Link>}
        <span className="mx-2">/</span>
        <span>{p.name}</span>
      </div>
      <div className="grid lg:grid-cols-2 gap-10">
        <div>
          <div className="aspect-square rounded-2xl overflow-hidden bg-afro-surface-alt">
            <img src={p.images[activeImg]} alt={p.name} className="w-full h-full object-cover" data-testid="pdp-image" />
          </div>
          {p.images.length > 1 && (
            <div className="flex gap-2 mt-3">
              {p.images.map((img, i) => (
                <button key={i} onClick={() => setActiveImg(i)} className={`w-16 h-16 rounded-md overflow-hidden border-2 ${i === activeImg ? "border-afro-primary" : "border-afro-border"}`}>
                  <img src={img} alt="" className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          )}
        </div>
        <div>
          {p.brand && <div className="text-xs uppercase tracking-widest text-afro-ink-soft">{p.brand}</div>}
          <h1 className="font-display text-3xl md:text-4xl text-afro-ink mt-1" data-testid="pdp-name">{p.name}</h1>
          <div className="flex items-center gap-2 mt-3 text-sm text-afro-ink-soft">
            <div className="flex gap-0.5">{[1,2,3,4,5].map(n => <Star key={n} size={14} fill="#D19C4C" stroke="#D19C4C" />)}</div>
            <span>{p.avg_rating?.toFixed?.(1)} · {p.review_count} reviews</span>
          </div>
          <div className="flex items-baseline gap-3 mt-5">
            <span className="text-3xl font-semibold text-afro-ink" data-testid="pdp-price">{formatGBP(price)}</span>
            {compareAt && compareAt > price && <span className="text-afro-ink-soft line-through">{formatGBP(compareAt)}</span>}
            {compareAt && compareAt > price && <span className="bg-afro-primary/10 text-afro-primary text-xs font-semibold px-2 py-0.5 rounded">Save {Math.round(((compareAt - price) / compareAt) * 100)}%</span>}
          </div>
          <p className="mt-5 text-afro-ink-soft leading-relaxed">{p.description}</p>

          {/* Variants */}
          {p.variants.length > 1 && (
            <div className="mt-6">
              <div className="text-sm font-medium mb-2">Pack size</div>
              <div className="flex flex-wrap gap-2">
                {p.variants.map(v => (
                  <button key={v.sku} onClick={() => setVariant(v)} className={`border rounded-md px-4 py-2 text-sm relative ${variant?.sku === v.sku ? "border-afro-primary bg-afro-primary/5" : "border-afro-border"}`} data-testid={`variant-${v.sku}`}>
                    {v.size_label}
                    <span className="block text-xs text-afro-ink-soft">{formatGBP(v.price)}</span>
                    {v.is_best_value && <span className="absolute -top-2 -right-2 bg-afro-accent text-afro-ink text-[9px] px-1.5 py-0.5 rounded font-semibold uppercase">Best value</span>}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="mt-6 flex items-center gap-4">
            <div className="flex items-center border border-afro-border rounded-md">
              <button onClick={() => setQty(Math.max(1, qty - 1))} className="w-10 h-10">−</button>
              <span className="w-10 text-center" data-testid="pdp-qty">{qty}</span>
              <button onClick={() => setQty(qty + 1)} className="w-10 h-10">+</button>
            </div>
            <button onClick={() => add(p.id, variant?.sku, qty)} className="afr-btn-primary flex-1 inline-flex items-center justify-center gap-2" disabled={p.stock === 0} data-testid="pdp-add-to-cart">
              <ShoppingBag size={18} /> Add to basket — {formatGBP(price * qty)}
            </button>
            <button onClick={toggleWish} className={`w-12 h-12 border rounded-md flex items-center justify-center ${wish ? "bg-afro-primary text-white border-afro-primary" : "border-afro-border text-afro-ink"}`} data-testid="pdp-wishlist">
              <Heart size={18} fill={wish ? "currentColor" : "none"} />
            </button>
          </div>

          <div className="grid sm:grid-cols-3 gap-3 mt-6 text-xs text-afro-ink-soft">
            <div className="flex gap-2 items-start"><Truck size={16} className="text-afro-primary" /> Free delivery over £50</div>
            <div className="flex gap-2 items-start"><Shield size={16} className="text-afro-primary" /> Authentic & fresh</div>
            <div className="flex gap-2 items-start"><RefreshCw size={16} className="text-afro-primary" /> Easy reorder</div>
          </div>

          {p.meal_tags?.length > 0 && (
            <div className="mt-6 p-4 bg-afro-surface-alt rounded-md text-sm">
              <div className="font-medium mb-1">Perfect for:</div>
              <div className="flex flex-wrap gap-2">
                {p.meal_tags.map(mt => (
                  <Link key={mt} to={`/meal/${mt.replace("_", "-")}-essentials`} className="bg-white border border-afro-border rounded-full px-3 py-1 text-xs hover:border-afro-primary">
                    {mt.replace("_", " ")}
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Reviews */}
      {data.reviews?.length > 0 && (
        <div className="mt-16" data-testid="pdp-reviews">
          <h2 className="font-display text-2xl mb-6">Customer reviews</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {data.reviews.map(r => (
              <div key={r.id} className="border border-afro-border rounded-xl p-5 bg-white">
                <div className="flex gap-0.5 mb-2">{[1,2,3,4,5].map(n => <Star key={n} size={14} fill={n <= r.rating ? "#D19C4C" : "transparent"} stroke="#D19C4C" />)}</div>
                <div className="font-semibold">{r.title}</div>
                <p className="text-sm text-afro-ink-soft mt-1">{r.body}</p>
                <div className="text-xs mt-3 text-afro-ink-soft">— {r.customer_name} · verified purchase</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Related products */}
      {data.related?.length > 0 && (
        <div className="mt-16" data-testid="pdp-related">
          <h2 className="font-display text-2xl mb-6">You might also like</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {data.related.slice(0, 4).map(r => <ProductCard key={r.id} product={r} />)}
          </div>
        </div>
      )}
    </div>
  );
}
