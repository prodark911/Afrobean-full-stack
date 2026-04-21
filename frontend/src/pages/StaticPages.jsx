import React from "react";
import { Link } from "react-router-dom";

function Pill({ children }) { return <span className="bg-afro-surface-alt text-afro-ink-soft rounded-full px-3 py-1 text-xs">{children}</span>; }

export function About() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-16" data-testid="about-page">
      <h1 className="font-display text-5xl">About Afrobean</h1>
      <p className="mt-4 text-afro-ink-soft text-lg leading-relaxed">Afrobean is Peterborough's premium African food supermarket — built for shoppers who want authentic products, easy meal-based discovery, smart cart building, and trusted pantry restocks.</p>
      <div className="mt-10 grid md:grid-cols-2 gap-8">
        <div>
          <h2 className="font-display text-2xl">Our mission</h2>
          <p className="mt-3 text-afro-ink-soft leading-relaxed">To make African food shopping as simple as ordering takeaway — authentic, modern, reliable, and proudly local to Peterborough.</p>
        </div>
        <div>
          <h2 className="font-display text-2xl">Our store</h2>
          <p className="mt-3 text-afro-ink-soft leading-relaxed">1227 Bourges Blvd, Peterborough PE1 2AU. We deliver within 5 miles of our store. Free delivery over £50.</p>
        </div>
      </div>
    </div>
  );
}

export function Delivery() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-16" data-testid="delivery-page">
      <h1 className="font-display text-5xl">Delivery information</h1>
      <div className="mt-10 space-y-6 text-afro-ink-soft leading-relaxed">
        <div className="bg-white border border-afro-border rounded-xl p-6">
          <h2 className="font-display text-2xl text-afro-ink">Peterborough local delivery</h2>
          <ul className="mt-3 list-disc pl-5 space-y-2">
            <li>We deliver within 5 miles of our store: 1227 Bourges Blvd, Peterborough PE1 2AU.</li>
            <li>£2.99 per mile delivery fee.</li>
            <li><strong>Free delivery</strong> on all orders over £50.</li>
            <li>Same-day and next-day slots available on select days.</li>
          </ul>
        </div>
        <div className="bg-white border border-afro-border rounded-xl p-6">
          <h2 className="font-display text-2xl text-afro-ink">Frozen & fresh</h2>
          <p className="mt-2">Frozen fish and meat are packed in insulated pouches and delivered within the time window selected at checkout.</p>
        </div>
      </div>
    </div>
  );
}

export function FAQ() {
  const qs = [
    ["Do you only deliver in Peterborough?", "Currently yes — within 5 miles of 1227 Bourges Blvd, Peterborough PE1 2AU. Expansion coming soon."],
    ["How does the AI meal assistant work?", "Tell Afrobean AI what you want to cook — for example, 'jollof rice for 5 people' — and it will assemble a basket of ingredients from our catalogue, which you can add to your cart in one click."],
    ["What payment methods do you accept?", "All major cards via Stripe, including Apple Pay and Google Pay."],
    ["Can I reorder my last basket?", "Yes — from your account page, tap 'Reorder' on any past order to quickly rebuild your basket."],
    ["How do bundles and meal collections differ?", "Meal collections are customisable baskets (swap items, pick servings). Bundles are pre-packaged savings — great for bulk and pantry restocks."],
    ["Do you ship frozen foods?", "Yes, within our local delivery area, in insulated packaging."],
  ];
  return (
    <div className="max-w-3xl mx-auto px-4 py-16" data-testid="faq-page">
      <h1 className="font-display text-5xl">Frequently asked questions</h1>
      <div className="mt-10 divide-y divide-afro-border bg-white border border-afro-border rounded-xl overflow-hidden">
        {qs.map(([q, a], i) => (
          <details key={i} className="p-6 group">
            <summary className="font-semibold cursor-pointer list-none flex items-center justify-between">{q}<span className="group-open:rotate-45 transition">+</span></summary>
            <p className="mt-3 text-afro-ink-soft">{a}</p>
          </details>
        ))}
      </div>
    </div>
  );
}

export function Contact() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-16" data-testid="contact-page">
      <h1 className="font-display text-5xl">Contact us</h1>
      <div className="mt-10 grid md:grid-cols-2 gap-6">
        <div className="bg-white border border-afro-border rounded-xl p-6">
          <h2 className="font-display text-2xl">WhatsApp</h2>
          <p className="mt-2 text-afro-ink-soft">Fastest way to reach us.</p>
          <a href="https://wa.me/447700900123" target="_blank" rel="noreferrer" className="afr-btn-primary inline-block mt-4">Chat on WhatsApp</a>
        </div>
        <div className="bg-white border border-afro-border rounded-xl p-6">
          <h2 className="font-display text-2xl">Visit the store</h2>
          <p className="mt-2 text-afro-ink-soft">1227 Bourges Blvd<br />Peterborough PE1 2AU</p>
          <p className="mt-2 text-afro-ink-soft">Open daily · 8am – 9pm</p>
        </div>
      </div>
    </div>
  );
}
