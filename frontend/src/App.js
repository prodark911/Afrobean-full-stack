import React from "react";
import { BrowserRouter, Routes, Route, Navigate, Outlet } from "react-router-dom";
import { AuthProvider, CartProvider, AdminProvider, useAdmin } from "./contexts";
import StorefrontLayout from "./components/StorefrontLayout";
import AdminLayout from "./components/AdminLayout";

import Home from "./pages/Home";
import Shop from "./pages/Shop";
import PDP from "./pages/PDP";
import MealCollection from "./pages/MealCollection";
import MealCollections from "./pages/MealCollections";
import AIAssistant from "./pages/AIAssistant";
import CartPage from "./pages/CartPage";
import Checkout from "./pages/Checkout";
import CheckoutSuccess from "./pages/CheckoutSuccess";
import Login from "./pages/Login";
import Account from "./pages/Account";
import { About, Delivery, FAQ, Contact } from "./pages/StaticPages";

import AdminLogin from "./pages/admin/AdminLogin";
import Dashboard from "./pages/admin/Dashboard";
import {
  AdminProducts, AdminProductEdit, AdminCategories, AdminCollections,
  AdminOrders, AdminOrderDetail, AdminCustomers, AdminInventory,
  AdminAIMapping, AdminBundles, AdminMessaging, AdminAnalytics,
  AdminImports, AdminAuditLogs, AdminDelivery, AdminSettings, AdminContent,
  AdminPricing, AdminMealCollections,
} from "./pages/admin/AdminPages";


function AdminGuard() {
  const { admin, loading } = useAdmin();
  if (loading) return <div className="p-16 text-center text-sm">Loading…</div>;
  if (!admin) return <Navigate to="/admin/login" />;
  return <AdminLayout />;
}


export default function App() {
  return (
    <BrowserRouter>
      <AdminProvider>
        <AuthProvider>
          <CartProvider>
            <Routes>
              {/* Storefront */}
              <Route element={<StorefrontLayout />}>
                <Route path="/" element={<Home />} />
                <Route path="/shop" element={<Shop mode="all" />} />
                <Route path="/search" element={<Shop mode="all" />} />
                <Route path="/category/:slug" element={<Shop mode="category" />} />
                <Route path="/collection/:slug" element={<Shop mode="collection" />} />
                <Route path="/p/:slug" element={<PDP />} />
                <Route path="/meal-collections" element={<MealCollections />} />
                <Route path="/meal/:slug" element={<MealCollection />} />
                <Route path="/ai-assistant" element={<AIAssistant />} />
                <Route path="/cart" element={<CartPage />} />
                <Route path="/checkout" element={<Checkout />} />
                <Route path="/checkout/success" element={<CheckoutSuccess />} />
                <Route path="/login" element={<Login />} />
                <Route path="/account" element={<Account />} />
                <Route path="/account/orders" element={<Account />} />
                <Route path="/about" element={<About />} />
                <Route path="/delivery" element={<Delivery />} />
                <Route path="/faq" element={<FAQ />} />
                <Route path="/contact" element={<Contact />} />
              </Route>

              {/* Admin */}
              <Route path="/admin/login" element={<AdminLogin />} />
              <Route path="/admin" element={<AdminGuard />}>
                <Route index element={<Navigate to="/admin/dashboard" />} />
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="products" element={<AdminProducts />} />
                <Route path="products/:id" element={<AdminProductEdit />} />
                <Route path="categories" element={<AdminCategories />} />
                <Route path="collections" element={<AdminCollections />} />
                <Route path="meal-collections" element={<AdminMealCollections />} />
                <Route path="ai-mapping" element={<AdminAIMapping />} />
                <Route path="bundles" element={<AdminBundles />} />
                <Route path="pricing" element={<AdminPricing />} />
                <Route path="inventory" element={<AdminInventory />} />
                <Route path="orders" element={<AdminOrders />} />
                <Route path="orders/:orderNumber" element={<AdminOrderDetail />} />
                <Route path="customers" element={<AdminCustomers />} />
                <Route path="messaging" element={<AdminMessaging />} />
                <Route path="content" element={<AdminContent />} />
                <Route path="analytics" element={<AdminAnalytics />} />
                <Route path="imports" element={<AdminImports />} />
                <Route path="delivery" element={<AdminDelivery />} />
                <Route path="audit" element={<AdminAuditLogs />} />
                <Route path="settings" element={<AdminSettings />} />
              </Route>

              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </CartProvider>
        </AuthProvider>
      </AdminProvider>
    </BrowserRouter>
  );
}
