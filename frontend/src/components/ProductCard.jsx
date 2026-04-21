import React from "react";
import { Link } from "react-router-dom";
import { formatGBP } from "../api";
import { useCart } from "../contexts";
import { ShoppingBag, Star } from "lucide-react";

export default function ProductCard({ product }) {
  const { add } = useCart();
  const p = product;
  const img = p.images?.[0];
  const saving = p.compare_at_price && p.compare_at_price > p.price ? Math.round(((p.compare_at_price - p.price) / p.compare_at_price) * 100) : 0;
  return (
    <div className="product-card bg-white rounded-xl overflow-hidden border border-afro-border" data-testid={`product-card-${p.slug}`}>
      <Link to={`/p/${p.slug}`} className="block relative overflow-hidden aspect-square bg-afro-surface-alt">
        {img && <img src={img} alt={p.name} className="w-full h-full object-cover" loading="lazy" />}
        {saving > 0 && <span className="absolute top-3 left-3 bg-afro-primary text-white text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider">Save {saving}%</span>}
        {p.bestseller && <span className="absolute top-3 right-3 bg-afro-accent text-afro-ink text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider">Bestseller</span>}
        {p.new_arrival && !p.bestseller && <span className="absolute top-3 right-3 bg-afro-secondary text-white text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider">New</span>}
        {p.stock === 0 && <div className="absolute inset-0 bg-black/50 flex items-center justify-center text-white font-semibold">Out of stock</div>}
      </Link>
      <div className="p-4">
        {p.brand && <div className="text-[11px] uppercase tracking-widest text-afro-ink-soft">{p.brand}</div>}
        <Link to={`/p/${p.slug}`} className="font-medium text-sm leading-snug line-clamp-2 block mt-1 min-h-[42px]">{p.name}</Link>
        <div className="flex items-center gap-1 mt-1 text-xs text-afro-ink-soft">
          <Star size={12} fill="#D19C4C" stroke="#D19C4C" />
          <span>{p.avg_rating?.toFixed?.(1) || "4.5"} · {p.review_count || 0}</span>
        </div>
        <div className="flex items-center justify-between mt-3">
          <div>
            <span className="font-semibold text-afro-ink" data-testid={`price-${p.slug}`}>{formatGBP(p.price)}</span>
            {p.compare_at_price && p.compare_at_price > p.price && (
              <span className="text-xs text-afro-ink-soft line-through ml-2">{formatGBP(p.compare_at_price)}</span>
            )}
          </div>
          <button onClick={() => add(p.id)} disabled={p.stock === 0} className="w-9 h-9 rounded-full bg-afro-primary text-white flex items-center justify-center hover:bg-afro-primary-hover disabled:bg-afro-border" data-testid={`add-${p.slug}`}>
            <ShoppingBag size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
