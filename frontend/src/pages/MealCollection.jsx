import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api, formatGBP } from "../api";
import { useCart } from "../contexts";

export default function MealCollection() {
  const { slug } = useParams();
  const { bulkAdd } = useCart();
  const [data, setData] = useState(null);
  const [servings, setServings] = useState(4);
  const [spice, setSpice] = useState("medium");
  const [selections, setSelections] = useState({}); // slot_key -> product_id

  useEffect(() => {
    api.get(`/meal-collections/${slug}`).then(r => {
      setData(r.data);
      setServings(r.data.meal_collection.servings_default || 4);
      // Default selections = first product in default_product_ids
      const s = {};
      const all = [...r.data.meal_collection.required_slots, ...r.data.meal_collection.optional_slots];
      all.forEach(slot => {
        if (slot.default_product_ids?.length) s[slot.slot_key] = slot.default_product_ids[0];
      });
      setSelections(s);
    });
  }, [slug]);

  if (!data) return <div className="p-16 text-center">Loading meal collection...</div>;
  const m = data.meal_collection;
  const prodMap = Object.fromEntries(data.products.map(p => [p.id, p]));

  const currentItems = () => {
    const items = [];
    m.required_slots.forEach(slot => {
      const pid = selections[slot.slot_key];
      if (pid && prodMap[pid]) items.push({ slot, product: prodMap[pid], required: true });
    });
    m.optional_slots.forEach(slot => {
      const pid = selections[slot.slot_key];
      if (pid && prodMap[pid]) items.push({ slot, product: prodMap[pid], required: false });
    });
    return items;
  };
  const total = currentItems().reduce((a, b) => a + b.product.price, 0);

  const addAll = async () => {
    const items = currentItems().map(i => ({ product_id: i.product.id, quantity: Math.max(1, Math.ceil(servings / 4)) }));
    await bulkAdd(items);
  };

  return (
    <div data-testid="meal-collection-page">
      <div className="relative h-[40vh] md:h-[50vh] overflow-hidden bg-afro-ink">
        <img src={m.hero_image} alt={m.title} className="absolute inset-0 w-full h-full object-cover opacity-70" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />
        <div className="relative max-w-7xl mx-auto px-4 h-full flex flex-col justify-end pb-10 text-white">
          <div className="text-xs uppercase tracking-widest text-afro-accent mb-2">Meal Collection</div>
          <h1 className="font-display text-4xl md:text-6xl">{m.title}</h1>
          <p className="mt-3 opacity-90 max-w-xl">{m.description}</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-10 grid lg:grid-cols-3 gap-10">
        <div className="lg:col-span-2">
          <div className="bg-white border border-afro-border rounded-2xl p-6 mb-8">
            <div className="grid sm:grid-cols-3 gap-4">
              <label className="block">
                <span className="text-xs uppercase tracking-widest text-afro-ink-soft">Servings</span>
                <input type="number" min={1} max={20} value={servings} onChange={e => setServings(+e.target.value)} className="afr-input mt-1" data-testid="servings-input" />
              </label>
              <label className="block">
                <span className="text-xs uppercase tracking-widest text-afro-ink-soft">Spice level</span>
                <select value={spice} onChange={e => setSpice(e.target.value)} className="afr-input mt-1" data-testid="spice-select">
                  <option value="mild">Mild</option>
                  <option value="medium">Medium</option>
                  <option value="hot">Hot</option>
                </select>
              </label>
              <div>
                <span className="text-xs uppercase tracking-widest text-afro-ink-soft">Tier</span>
                <div className="mt-1 text-sm font-medium capitalize">{m.tier}</div>
              </div>
            </div>
          </div>

          <h2 className="font-display text-2xl mb-4">Required ingredients</h2>
          <div className="space-y-3">
            {m.required_slots.map(slot => (
              <SlotRow key={slot.slot_key} slot={slot} prodMap={prodMap} selection={selections[slot.slot_key]}
                onChange={pid => setSelections(s => ({ ...s, [slot.slot_key]: pid }))} required />
            ))}
          </div>

          {m.optional_slots?.length > 0 && (
            <>
              <h2 className="font-display text-2xl mt-10 mb-4">Optional additions</h2>
              <div className="space-y-3">
                {m.optional_slots.map(slot => (
                  <SlotRow key={slot.slot_key} slot={slot} prodMap={prodMap} selection={selections[slot.slot_key]}
                    onChange={pid => setSelections(s => ({ ...s, [slot.slot_key]: pid }))} />
                ))}
              </div>
            </>
          )}
        </div>

        <aside className="lg:sticky lg:top-28 h-fit bg-afro-surface-alt rounded-2xl p-6 border border-afro-border" data-testid="meal-summary">
          <h3 className="font-display text-2xl">Your basket</h3>
          <p className="text-xs text-afro-ink-soft">For {servings} servings · {spice} spice</p>
          <div className="mt-4 divide-y divide-afro-border">
            {currentItems().map(i => (
              <div key={i.product.id} className="flex justify-between py-2 text-sm">
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{i.product.name}</div>
                  <div className="text-xs text-afro-ink-soft">{i.slot.label}{!i.required && " · optional"}</div>
                </div>
                <div className="font-semibold ml-3">{formatGBP(i.product.price)}</div>
              </div>
            ))}
          </div>
          <div className="flex justify-between py-3 mt-3 border-t border-afro-border font-semibold">
            <span>Estimated total</span>
            <span data-testid="meal-total">{formatGBP(total)}</span>
          </div>
          <button onClick={addAll} className="afr-btn-primary w-full mt-3" data-testid="add-all-to-cart">Add all to basket</button>
          {total < 50 && <p className="text-xs text-afro-ink-soft mt-3 text-center">Spend {formatGBP(50 - total)} more for free delivery.</p>}
        </aside>
      </div>
    </div>
  );
}

function SlotRow({ slot, prodMap, selection, onChange, required = false }) {
  const options = [...(slot.default_product_ids || []), ...(slot.substitute_product_ids || [])]
    .map(id => prodMap[id]).filter(Boolean);
  const selected = prodMap[selection];
  return (
    <div className="bg-white border border-afro-border rounded-xl p-4 flex flex-col md:flex-row md:items-center gap-4" data-testid={`slot-${slot.slot_key}`}>
      <div className="md:w-48">
        <div className="text-xs uppercase tracking-widest text-afro-primary">{required ? "Required" : "Optional"}</div>
        <div className="font-medium">{slot.label}</div>
      </div>
      <div className="flex-1 flex items-center gap-3">
        {selected?.images?.[0] && <img src={selected.images[0]} alt="" className="w-14 h-14 rounded-md object-cover" />}
        <select value={selection || ""} onChange={e => onChange(e.target.value)} className="afr-input flex-1" data-testid={`slot-select-${slot.slot_key}`}>
          <option value="">— None —</option>
          {options.map(p => <option key={p.id} value={p.id}>{p.name} ({prodMap[p.id]?.price ? "£"+p.price : ""})</option>)}
        </select>
      </div>
    </div>
  );
}
