import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

export default function MealCollections() {
  const [items, setItems] = useState([]);
  useEffect(() => { api.get("/meal-collections").then(r => setItems(r.data)); }, []);
  return (
    <div className="max-w-7xl mx-auto px-4 py-12" data-testid="meal-collections-index">
      <div className="mb-10">
        <div className="text-xs uppercase tracking-widest text-afro-primary">Meal collections</div>
        <h1 className="font-display text-4xl md:text-5xl text-afro-ink mt-2">Cook like a pro, shop like a shortcut.</h1>
        <p className="text-afro-ink-soft mt-3 max-w-xl">Every meal collection is a curated basket of essentials you can customise, resize, and add to your cart in one click.</p>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {items.map(m => (
          <Link key={m.slug} to={`/meal/${m.slug}`} className="group relative rounded-2xl overflow-hidden aspect-[4/5] bg-afro-ink" data-testid={`meal-card-${m.slug}`}>
            <img src={m.hero_image} alt={m.title} className="absolute inset-0 w-full h-full object-cover opacity-90 group-hover:opacity-100 group-hover:scale-105 transition duration-500" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/85 via-black/30 to-transparent" />
            <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
              <div className="text-xs uppercase tracking-widest text-afro-accent">{m.servings_default} servings · {m.required_slots?.length || 0} essentials</div>
              <h3 className="font-display text-2xl md:text-3xl mt-2">{m.title}</h3>
              <p className="text-sm opacity-80 mt-2 line-clamp-2">{m.description}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
