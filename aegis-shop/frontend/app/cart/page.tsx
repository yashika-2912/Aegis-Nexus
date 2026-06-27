"use client";

import { useState } from "react";
import Header from "@/components/Header";
import { useAuth, useCart } from "@/lib/store";
import { buyNow } from "@/lib/api";
import Link from "next/link";

export default function CartPage() {
  const { items, removeItem, clear, total } = useCart();
  const { email } = useAuth();
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function checkout() {
    if (!email || items.length === 0) return;
    setChecking(true); setError(""); setSuccess("");
    try {
      for (const item of items) {
        const result = await buyNow({
          product_id: item.id, product_name: item.name,
          price: item.price, quantity: item.quantity, user_email: email,
        });
        setSuccess(prev => prev + `Order ${result.order.order_id} ✓ `);
      }
      clear();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Checkout failed");
    } finally {
      setChecking(false);
    }
  }

  return (
    <div className="min-h-screen">
      <Header />
      <main className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Shopping Cart</h1>
        {items.length === 0 ? (
          <p className="text-gray-500">Your cart is empty. <Link href="/" className="text-indigo-600 hover:underline">Browse products</Link></p>
        ) : (
          <>
            <div className="space-y-4">
              {items.map(item => (
                <div key={item.id} className="flex justify-between items-center p-4 bg-white rounded-lg border">
                  <div>
                    <p className="font-medium">{item.name}</p>
                    <p className="text-sm text-gray-500">Qty: {item.quantity} × ${item.price.toFixed(2)}</p>
                  </div>
                  <button onClick={() => removeItem(item.id)} className="text-red-500 text-sm hover:underline">Remove</button>
                </div>
              ))}
            </div>
            <div className="mt-6 p-4 bg-white rounded-lg border">
              <p className="text-xl font-bold">Total: ${total.toFixed(2)}</p>
              {!email && <p className="text-amber-600 text-sm mt-2"><Link href="/login" className="underline">Login</Link> to checkout</p>}
              {error && <p className="text-red-600 mt-2">{error}</p>}
              {success && <p className="text-green-600 mt-2">{success}</p>}
              <button onClick={checkout} disabled={checking || !email}
                className="mt-4 w-full py-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50">
                {checking ? "Processing..." : "Checkout"}
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
