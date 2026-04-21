import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, formatGBP } from "../api";
import ProductCard from "../components/ProductCard";
import { Sparkles, Truck, Shield, Clock, Star, ChevronRight, MessageCircle } from "lucide-react";

const MEAL_IMG = {
  "jollof-rice-essentials": "https://images.pexels.com/photos/36707708/pexels-photo-36707708.jpeg?auto=compress&cs=tinysrgb&w=900",
  "pepper-soup-essentials": "https://images.unsplash.com/photo-1583835746434-cf1534674b41?w=900&q=80",
  "moi-moi-essentials": "https://images.unsplash.com/photo-1515543904379-3d757afe72e4?w=900&q=80",
  "banga-soup-essentials": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=900&q=80",
  "efo-riro-essentials": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=900&q=80",
  "breakfast-staples": "https://images.unsplash.com/photo-1517686469429-8bdb88b9f907?w=900&q=80",
};

export default function Home() {
  const [cats, setCats] = useState([]);
  const [mealColls, setMealColls] = useState([]);
  const [bestSellers, setBestSellers] = useState([]);
  const [newArrivals, setNewArrivals] = useState([]);
  const [bundles, setBundles] = useState([]);
  const [reviews, setReviews] = useState([]);

  useEffect(() => {
    api.get("/categories").then(r => setCats(r.data));
    api.get("/meal-collections").then(r => setMealColls(r.data));
    api.get("/products", { params: { bestseller: true, limit: 8 } }).then(r => setBestSellers(r.data.items));
    api.get("/products", { params: { new_arrival: true, limit: 8 } }).then(r => setNewArrivals(r.data.items));
    api.get("/bundles").then(r => setBundles(r.data.slice(0, 3)));
    api.get("/reviews", { params: { limit: 6 } }).then(r => setReviews(r.data));
  }, []);

  return (
    <div data-testid="home-page">
      {/* HERO */}
      <section className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 pt-12 pb-16 md:pt-20 md:pb-24 grid lg:grid-cols-5 gap-10 items-center">
          <div className="lg:col-span-3 relative z-10" data-testid="hero">
            <div className="inline-flex items-center gap-2 bg-afro-surface-alt border border-afro-border rounded-full px-3 py-1 text-xs uppercase tracking-widest text-afro-primary mb-6">
              <span className="w-1.5 h-1.5 rounded-full bg-afro-primary animate-pulse" /> Now delivering in Peterborough
            </div>
            <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl leading-[1.05] tracking-tight text-afro-ink">
              Your premium <br className="hidden md:block" />
              <span className="italic text-afro-primary">African food supermarket</span><br className="hidden md:block" />
              in Peterborough
            </h1>
            <p className="mt-6 text-afro-ink-soft text-lg leading-relaxed max-w-2xl">
              Shop authentic African groceries, frozen foods, pantry staples, snacks, beauty, and household essentials — all in one place. Discover what to cook, find the right ingredients fast, and get everything you need delivered to your door.
            </p>
            <p className="mt-3 text-afro-ink-soft text-sm max-w-xl">
              From jollof rice essentials and pepper soup ingredients to breakfast staples, swallows, oils, spices, frozen fish, and family pantry packs — Afrobean makes African food shopping simple, modern, and reliable.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row gap-3" data-testid="hero-ctas">
              <Link to="/shop" className="afr-btn-primary inline-flex items-center gap-2" data-testid="hero-shop-cta">
                Shop All Products <ChevronRight size={18} />
              </Link>
              <Link to="/ai-assistant" className="afr-btn-outline inline-flex items-center gap-2" data-testid="hero-ai-cta">
                <Sparkles size={16} /> Ask Afrobean AI What to Cook
              </Link>
            </div>
            <div className="mt-10 grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { i: <Truck size={18} />, t: "Free delivery", s: "over £50 · Peterborough only" },
                { i: <Sparkles size={18} />, t: "AI meal assistant", s: "Recipe-to-cart" },
                { i: <Shield size={18} />, t: "Authentic brands", s: "Quality African groceries" },
                { i: <Clock size={18} />, t: "Fast checkout", s: "Modern, easy, mobile-first" },
              ].map((x, i) => (
                <div key={i} className="flex gap-3 items-start text-sm">
                  <div className="w-9 h-9 rounded-md bg-afro-surface-alt text-afro-primary flex items-center justify-center flex-shrink-0">{x.i}</div>
                  <div><div className="font-semibold">{x.t}</div><div className="text-afro-ink-soft text-xs">{x.s}</div></div>
                </div>
              ))}
            </div>
            <div className="mt-8 flex flex-wrap items-center gap-4 text-xs text-afro-ink-soft">
              <div className="flex items-center gap-1">
                {[1,2,3,4,5].map(n => <Star key={n} size={14} fill="#D19C4C" stroke="#D19C4C" />)}
                <span className="ml-1">Rated 4.8/5 on Google & Trustpilot</span>
              </div>
            </div>
          </div>
          <div className="lg:col-span-2 relative" data-testid="hero-image">
            <div className="aspect-[4/5] rounded-2xl overflow-hidden bg-afro-surface-alt relative">
              <img src="https://images.unsplash.com/photo-1760445529457-07cc50d201d3?w=900&q=80" alt="Premium African groceries" className="w-full h-full object-cover" />
              <div className="grain-overlay" />
            </div>
            <div className="absolute -bottom-6 -left-6 bg-white shadow-pop rounded-2xl p-4 flex items-center gap-3 border border-afro-border hidden md:flex">
              <div className="w-12 h-12 rounded-full bg-afro-primary flex items-center justify-center text-white"><Sparkles size={20} /></div>
              <div>
                <div className="text-xs text-afro-ink-soft">Ask Afrobean AI</div>
                <div className="font-medium text-sm">"Jollof rice for 5 people"</div>
              </div>
            </div>
            <div className="absolute -top-6 -right-6 bg-afro-ink text-afro-bg rounded-full w-28 h-28 flex items-center justify-center text-center text-xs font-semibold leading-tight rotate-badge hidden md:flex">
              Free delivery · over £50
            </div>
          </div>
        </div>
      </section>

      {/* CATEGORY GRID */}
      <section className="max-w-7xl mx-auto px-4 py-14" data-testid="categories-section">
        <div className="flex items-end justify-between mb-8">
          <div>
            <h2 className="font-display text-3xl md:text-4xl text-afro-ink">Shop by category</h2>
            <p className="text-afro-ink-soft mt-1">Everything from rice and swallows to frozen fish and beauty.</p>
          </div>
          <Link to="/shop" className="hidden md:inline text-sm font-medium text-afro-primary hover:underline">View all →</Link>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 stagger">
          {cats.slice(0, 8).map(c => (
            <Link key={c.slug} to={`/category/${c.slug}`} className="category-tile group relative rounded-2xl overflow-hidden aspect-[4/3] bg-afro-surface-alt border border-afro-border" data-testid={`home-cat-${c.slug}`}>
              {c.image && <img src={c.image} alt="" className="absolute inset-0 w-full h-full object-cover opacity-80 group-hover:opacity-100 transition" />}
              <div className="absolute inset-0 bg-gradient-to-t from-afro-ink/80 via-afro-ink/20 to-transparent" />
              <div className="absolute bottom-4 left-4 right-4 text-white">
                <div className="font-display text-xl font-medium">{c.name}</div>
                <div className="text-xs opacity-80">{c.product_count} products →</div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* AI ASSISTANT CALLOUT */}
      <section className="max-w-7xl mx-auto px-4 py-12" data-testid="ai-section">
        <div className="relative rounded-3xl overflow-hidden bg-afro-ink text-afro-bg p-8 md:p-14 grid lg:grid-cols-2 gap-8 items-center">
          <div>
            <div className="inline-flex items-center gap-2 bg-white/10 rounded-full px-3 py-1 text-xs uppercase tracking-widest mb-4">
              <Sparkles size={12} /> New · Afrobean AI
            </div>
            <h2 className="font-display text-3xl md:text-5xl leading-tight">Tell Afrobean AI what you want to cook.</h2>
            <p className="mt-4 text-afro-bg/80 leading-relaxed max-w-xl">
              Get ingredient suggestions, serving-size help, smart substitutions, and one-click add-to-cart recommendations — built for African cooking.
            </p>
            <div className="mt-6 flex flex-wrap gap-2">
              {["What do I need to cook jollof rice for 5 people?", "Help me make pepper soup.", "What can I use for moi moi?", "I want breakfast staples for the week."].map((p, i) => (
                <Link key={i} to={`/ai-assistant?q=${encodeURIComponent(p)}`} className="bg-white/10 hover:bg-white/20 rounded-full px-3 py-1.5 text-xs transition" data-testid={`ai-suggestion-${i}`}>{p}</Link>
              ))}
            </div>
            <Link to="/ai-assistant" className="mt-8 inline-flex items-center gap-2 bg-afro-accent text-afro-ink font-semibold px-6 py-3 rounded-md hover:bg-white transition" data-testid="ai-main-cta">
              Open Afrobean AI <ChevronRight size={18} />
            </Link>
          </div>
          <div className="relative">
            <div className="bg-afro-bg text-afro-ink rounded-2xl p-5 shadow-pop max-w-md ml-auto">
              <div className="flex items-center gap-2 text-xs text-afro-ink-soft mb-3"><div className="w-7 h-7 rounded-full bg-afro-primary text-white flex items-center justify-center text-xs">AI</div>Afrobean AI · just now</div>
              <p className="text-sm leading-relaxed">For jollof rice serving 5, you'll need long-grain rice, tomato paste, jollof spice mix, curry, thyme, stock seasoning, and protein of choice. I've built a basket for £28.40 — would you like to add everything?</p>
              <button className="mt-4 bg-afro-primary text-white text-sm px-4 py-2 rounded-md w-full">Add all to basket · £28.40</button>
            </div>
          </div>
        </div>
      </section>

      {/* BEST SELLERS */}
      <section className="max-w-7xl mx-auto px-4 py-14" data-testid="bestsellers-section">
        <div className="flex items-end justify-between mb-8">
          <div>
            <div className="text-xs uppercase tracking-widest text-afro-primary">Best Sellers</div>
            <h2 className="font-display text-3xl md:text-4xl text-afro-ink">Peterborough's favourites</h2>
          </div>
          <Link to="/collection/best-sellers" className="text-sm font-medium text-afro-primary hover:underline">View all →</Link>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {bestSellers.map(p => <ProductCard key={p.id} product={p} />)}
        </div>
      </section>

      {/* MEAL COLLECTIONS */}
      <section className="bg-afro-surface-alt py-14" data-testid="meal-collections-section">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-end justify-between mb-8">
            <div>
              <div className="text-xs uppercase tracking-widest text-afro-primary">Meal collections</div>
              <h2 className="font-display text-3xl md:text-4xl text-afro-ink">Cook with confidence</h2>
            </div>
            <Link to="/meal-collections" className="text-sm font-medium text-afro-primary hover:underline">All meals →</Link>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {mealColls.map(m => (
              <Link key={m.slug} to={`/meal/${m.slug}`} className="group relative rounded-2xl overflow-hidden aspect-[4/5] bg-afro-ink" data-testid={`home-meal-${m.slug}`}>
                <img src={MEAL_IMG[m.slug] || m.hero_image} alt={m.title} className="absolute inset-0 w-full h-full object-cover opacity-90 group-hover:opacity-100 group-hover:scale-105 transition duration-500" />
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
      </section>

      {/* FREE DELIVERY BANNER */}
      <section className="max-w-7xl mx-auto px-4 py-14" data-testid="free-delivery-banner">
        <div className="rounded-3xl bg-afro-primary text-white p-10 md:p-16 relative overflow-hidden">
          <div className="grain-overlay" />
          <div className="relative grid md:grid-cols-2 gap-8 items-center">
            <div>
              <h2 className="font-display text-3xl md:text-5xl leading-tight">Spend £50.<br />Delivery's on us.</h2>
              <p className="mt-4 text-white/80 max-w-md">Free delivery in Peterborough when your basket hits £50. Otherwise, £2.99 per mile up to 5 miles from our store.</p>
            </div>
            <div className="flex md:justify-end">
              <Link to="/shop" className="bg-white text-afro-primary px-6 py-3 rounded-md font-semibold hover:bg-afro-bg transition" data-testid="free-delivery-cta">Start shopping</Link>
            </div>
          </div>
        </div>
      </section>

      {/* WEEKLY DEALS / BUNDLES */}
      <section className="max-w-7xl mx-auto px-4 py-14" data-testid="bundles-section">
        <div className="flex items-end justify-between mb-8">
          <div>
            <div className="text-xs uppercase tracking-widest text-afro-primary">Weekly deals</div>
            <h2 className="font-display text-3xl md:text-4xl">Pantry restock & value packs</h2>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {bundles.map(b => (
            <Link key={b.slug} to={`/bundle/${b.slug}`} className="group relative rounded-2xl overflow-hidden border border-afro-border bg-white" data-testid={`bundle-${b.slug}`}>
              <div className="aspect-[5/4] bg-afro-surface-alt overflow-hidden">
                {b.image && <img src={b.image} alt={b.title} className="w-full h-full object-cover group-hover:scale-105 transition duration-500" />}
              </div>
              <div className="p-5">
                <div className="text-xs uppercase tracking-widest text-afro-primary">{b.tier} bundle</div>
                <h3 className="font-display text-2xl mt-1">{b.title}</h3>
                <p className="text-sm text-afro-ink-soft mt-2 line-clamp-2">{b.description}</p>
                <div className="mt-3 flex items-center gap-2">
                  <span className="font-semibold">{formatGBP(b.price)}</span>
                  {b.compare_at_price && <span className="text-sm text-afro-ink-soft line-through">{formatGBP(b.compare_at_price)}</span>}
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* WHY AFROBEAN */}
      <section className="max-w-7xl mx-auto px-4 py-14 grid md:grid-cols-4 gap-6" data-testid="why-section">
        {[
          { i: "fa-seedling", t: "Authentic range", s: "Hand-picked African brands you trust." },
          { i: "fa-wand-magic-sparkles", t: "Easy meal shopping", s: "Recipe-to-cart in a few clicks." },
          { i: "fa-bolt", t: "Modern convenience", s: "Built mobile-first for fast shopping." },
          { i: "fa-house-chimney-user", t: "For real households", s: "Pack sizes that fit weekly family cooking." },
        ].map((x, i) => (
          <div key={i} className="bg-white rounded-2xl p-6 border border-afro-border">
            <i className={`fa-solid ${x.i} text-afro-primary text-2xl`} />
            <h3 className="font-display text-xl mt-4">{x.t}</h3>
            <p className="text-sm text-afro-ink-soft mt-2">{x.s}</p>
          </div>
        ))}
      </section>

      {/* RECIPES */}
      <section className="bg-afro-ink text-afro-bg py-14" data-testid="recipes-section">
        <div className="max-w-7xl mx-auto px-4 grid lg:grid-cols-2 gap-8 items-center">
          <div>
            <div className="text-xs uppercase tracking-widest text-afro-accent">Recipe inspiration</div>
            <h2 className="font-display text-3xl md:text-5xl mt-2">Cook jollof with confidence.<br />Make pepper soup your way.</h2>
            <p className="mt-4 text-afro-bg/80 max-w-lg">Simple, reliable recipes for African classics — paired with one-click shopping lists.</p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {[
              "https://images.pexels.com/photos/36707708/pexels-photo-36707708.jpeg?auto=compress&cs=tinysrgb&w=900",
              "https://images.unsplash.com/photo-1583835746434-cf1534674b41?w=900&q=80",
            ].map((u, i) => (
              <div key={i} className="aspect-[4/5] rounded-2xl overflow-hidden"><img src={u} alt="" className="w-full h-full object-cover hover:scale-105 transition duration-500" /></div>
            ))}
          </div>
        </div>
      </section>

      {/* NEW ARRIVALS */}
      <section className="max-w-7xl mx-auto px-4 py-14" data-testid="newarrivals-section">
        <div className="flex items-end justify-between mb-8">
          <div>
            <div className="text-xs uppercase tracking-widest text-afro-primary">New arrivals</div>
            <h2 className="font-display text-3xl md:text-4xl">Fresh to the shelves</h2>
          </div>
          <Link to="/collection/new-arrivals" className="text-sm font-medium text-afro-primary hover:underline">View all →</Link>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {newArrivals.map(p => <ProductCard key={p.id} product={p} />)}
        </div>
      </section>

      {/* REVIEWS */}
      <section className="bg-afro-surface-alt py-14" data-testid="reviews-section">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-end justify-between mb-8">
            <div>
              <div className="text-xs uppercase tracking-widest text-afro-primary">What shoppers say</div>
              <h2 className="font-display text-3xl md:text-4xl">Loved by Peterborough families</h2>
            </div>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {reviews.map(r => (
              <div key={r.id} className="bg-white p-6 rounded-2xl border border-afro-border">
                <div className="flex gap-1 mb-2">
                  {[1,2,3,4,5].map(n => <Star key={n} size={14} fill={n <= r.rating ? "#D19C4C" : "transparent"} stroke="#D19C4C" />)}
                </div>
                <div className="font-display text-lg mb-2">{r.title}</div>
                <p className="text-sm text-afro-ink-soft">{r.body}</p>
                <div className="mt-4 text-xs text-afro-ink-soft">— {r.customer_name}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* WhatsApp Support */}
      <section className="max-w-7xl mx-auto px-4 py-14" data-testid="whatsapp-section">
        <div className="rounded-3xl bg-[#25D366]/10 border border-[#25D366]/30 p-8 md:p-12 flex flex-col md:flex-row items-center gap-6">
          <div className="flex-1">
            <h3 className="font-display text-2xl md:text-3xl">Need help finding something?</h3>
            <p className="text-afro-ink-soft mt-2">Chat with us on WhatsApp — our team usually replies within minutes during store hours.</p>
          </div>
          <a href="https://wa.me/447700900123" target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 bg-[#25D366] text-white px-6 py-3 rounded-md font-semibold" data-testid="whatsapp-cta">
            <MessageCircle size={18} /> Chat on WhatsApp
          </a>
        </div>
      </section>

      {/* FINAL CTA */}
      <section className="max-w-7xl mx-auto px-4 pb-20" data-testid="final-cta">
        <div className="rounded-3xl bg-afro-primary text-white p-10 md:p-16 text-center relative overflow-hidden">
          <div className="grain-overlay" />
          <h2 className="font-display text-3xl md:text-5xl relative">Everything you need for African cooking, all in one modern supermarket.</h2>
          <div className="mt-8 flex flex-col sm:flex-row gap-3 justify-center relative">
            <Link to="/shop" className="bg-white text-afro-primary px-6 py-3 rounded-md font-semibold">Shop All Products</Link>
            <Link to="/ai-assistant" className="border border-white/40 text-white px-6 py-3 rounded-md font-semibold">Ask Afrobean AI</Link>
          </div>
        </div>
      </section>
    </div>
  );
}
