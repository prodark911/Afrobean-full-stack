import React, { useState } from "react";
import { Link } from "react-router-dom";
import { MessageCircle } from "lucide-react";

export default function Footer() {
  const [email, setEmail] = useState("");
  const subscribe = (e) => { e.preventDefault(); alert(`Subscribed: ${email}`); setEmail(""); };
  return (
    <footer className="bg-afro-ink text-afro-bg mt-20" data-testid="footer">
      <div className="max-w-7xl mx-auto px-4 py-16 grid lg:grid-cols-5 md:grid-cols-3 gap-10">
        <div className="lg:col-span-2">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-9 h-9 rounded-lg bg-afro-primary flex items-center justify-center text-afro-bg font-display font-bold text-xl">A</div>
            <span className="font-display text-2xl">Afrobean</span>
          </div>
          <p className="text-afro-bg/70 text-sm leading-relaxed max-w-sm">
            Peterborough's premium African food supermarket. Authentic groceries, smart meal-to-cart shopping, and fast local delivery.
          </p>
          <form onSubmit={subscribe} className="mt-6 flex gap-2" data-testid="newsletter-form">
            <input
              type="email" required value={email} onChange={e => setEmail(e.target.value)}
              placeholder="Enter your email"
              className="flex-1 bg-white/10 border border-white/20 rounded-md px-3 py-2 text-sm placeholder:text-afro-bg/50 focus:outline-none focus:border-afro-accent"
              data-testid="newsletter-email"
            />
            <button type="submit" className="bg-afro-accent text-afro-ink px-4 py-2 rounded-md text-sm font-semibold hover:bg-white transition" data-testid="newsletter-submit">Subscribe</button>
          </form>
        </div>
        <div>
          <h4 className="text-sm font-semibold uppercase tracking-wide mb-4">Shop</h4>
          <ul className="space-y-2 text-sm text-afro-bg/70">
            <li><Link to="/shop" data-testid="footer-shop-all">Shop All</Link></li>
            <li><Link to="/meal-collections" data-testid="footer-meal-collections">Meal Collections</Link></li>
            <li><Link to="/collection/best-sellers">Best Sellers</Link></li>
            <li><Link to="/collection/new-arrivals">New Arrivals</Link></li>
            <li><Link to="/collection/pantry-restock">Deals</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="text-sm font-semibold uppercase tracking-wide mb-4">Help</h4>
          <ul className="space-y-2 text-sm text-afro-bg/70">
            <li><Link to="/delivery" data-testid="footer-delivery">Delivery Information</Link></li>
            <li><Link to="/about" data-testid="footer-about">About Afrobean</Link></li>
            <li><Link to="/contact">Contact Us</Link></li>
            <li><Link to="/faq">FAQs</Link></li>
            <li><a href="https://wa.me/447700900123" target="_blank" rel="noreferrer" data-testid="footer-whatsapp">WhatsApp Support</a></li>
          </ul>
        </div>
        <div>
          <h4 className="text-sm font-semibold uppercase tracking-wide mb-4">Legal</h4>
          <ul className="space-y-2 text-sm text-afro-bg/70">
            <li><Link to="/faq">Privacy Policy</Link></li>
            <li><Link to="/faq">Terms & Conditions</Link></li>
          </ul>
          <div className="mt-6 text-xs text-afro-bg/50 leading-relaxed">
            1227 Bourges Blvd<br />Peterborough PE1 2AU, UK
          </div>
        </div>
      </div>
      <div className="border-t border-white/10 px-4 py-5 text-center text-xs text-afro-bg/50">
        © {new Date().getFullYear()} Afrobean. All rights reserved. · Currency: GBP (£)
      </div>
      <a href="https://wa.me/447700900123" target="_blank" rel="noreferrer" className="fixed bottom-6 right-6 z-40 bg-[#25D366] text-white w-14 h-14 rounded-full flex items-center justify-center shadow-pop hover:scale-105 transition" data-testid="floating-whatsapp">
        <MessageCircle size={24} />
      </a>
    </footer>
  );
}
