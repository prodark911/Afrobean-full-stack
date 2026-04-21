import React, { useEffect, useState } from "react";
import { useSearchParams, useParams } from "react-router-dom";
import { api } from "../api";
import ProductCard from "../components/ProductCard";

export default function Shop({ mode = "all" }) {
  const [params, setParams] = useSearchParams();
  const { slug } = useParams();
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [meta, setMeta] = useState(null); // category or collection
  const [sort, setSort] = useState(params.get("sort") || "bestseller");
  const q = params.get("q") || "";

  useEffect(() => {
    const load = async () => {
      if (mode === "category" && slug) {
        const { data } = await api.get(`/categories/${slug}`);
        setMeta({ type: "category", ...data.category });
        setItems(data.products);
        setTotal(data.products.length);
      } else if (mode === "collection" && slug) {
        const { data } = await api.get(`/collections/${slug}`);
        setMeta({ type: "collection", ...data.collection });
        setItems(data.products);
        setTotal(data.products.length);
      } else {
        const { data } = await api.get("/products", { params: { q, sort, limit: 60 } });
        setItems(data.items); setTotal(data.total);
        setMeta({ type: "shop", title: q ? `Search results for "${q}"` : "Shop All Products",
                  description: q ? "" : "Browse the full Afrobean catalogue." });
      }
    };
    load();
  }, [slug, mode, q, sort]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-10" data-testid="shop-page">
      <div className="mb-8">
        <div className="text-xs uppercase tracking-widest text-afro-primary mb-2">{meta?.type === "collection" ? "Collection" : meta?.type === "category" ? "Category" : "Catalogue"}</div>
        <h1 className="font-display text-3xl md:text-5xl text-afro-ink">{meta?.name || meta?.title || "Shop All"}</h1>
        {meta?.description && <p className="text-afro-ink-soft mt-3 max-w-2xl">{meta.description}</p>}
      </div>
      <div className="flex items-center justify-between mb-6">
        <span className="text-sm text-afro-ink-soft" data-testid="results-count">{total} products</span>
        <select className="afr-input max-w-[180px] text-sm" value={sort} onChange={e => { setSort(e.target.value); setParams(p => { p.set("sort", e.target.value); return p; }); }} data-testid="sort-select">
          <option value="bestseller">Bestsellers</option>
          <option value="price_asc">Price: Low → High</option>
          <option value="price_desc">Price: High → Low</option>
          <option value="newest">Newest</option>
          <option value="name">Name A-Z</option>
        </select>
      </div>
      {items.length === 0 ? (
        <div className="py-20 text-center text-afro-ink-soft">No products found. Try a different search.</div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {items.map(p => <ProductCard key={p.id} product={p} />)}
        </div>
      )}
    </div>
  );
}
