"use client";

import { useEffect, useState } from "react";
import Header from "@/components/Header";
import { getProducts, buyNow, runLoadGenerator, toggleRoute, Product } from "@/lib/api";
import { useAuth, useCart } from "@/lib/store";
import Link from "next/link";

export default function HomePage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [buying, setBuying] = useState<string | null>(null);
  const [buyError, setBuyError] = useState("");
  const [buySuccess, setBuySuccess] = useState("");
  const { email } = useAuth();
  const { addItem } = useCart();

  useEffect(() => { loadProducts(); }, []);

  async function loadProducts() {
    setLoading(true); setError("");
    try {
      setProducts(await getProducts());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  }

  async function handleBuyNow(p: Product) {
    if (!email) { setBuyError("Please login first"); return; }
    setBuying(p.id); setBuyError(""); setBuySuccess("");
    try {
      const result = await buyNow({
        product_id: p.id, product_name: p.name,
        price: p.price, quantity: 1, user_email: email,
      });
      setBuySuccess(`Order ${result.order.order_id} placed! Payment ${result.payment.payment_id}`);
    } catch (e: unknown) {
      setBuyError(e instanceof Error ? e.message : "Checkout failed");
    } finally {
      setBuying(null);
    }
  }

  return (
    <div className="min-h-screen">
      <Header />
      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Enterprise Security & Observability</h1>
          <p className="text-gray-600">Premium tools for modern infrastructure teams.</p>
        </div>

        {buyError && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">{buyError}</div>
        )}
        {buySuccess && (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg">{buySuccess}</div>
        )}

        {loading && <p className="text-gray-500">Loading products...</p>}
        {error && (
          <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700 font-medium">{error}</p>
            <button onClick={loadProducts} className="mt-2 text-indigo-600 hover:underline">Retry</button>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map(p => (
            <div key={p.id} className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition">
              <div className="h-40 bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center">
                <span className="text-4xl">🛡️</span>
              </div>
              <div className="p-5">
                <h3 className="font-semibold text-lg">{p.name}</h3>
                <p className="text-gray-500 text-sm mt-1">{p.description}</p>
                <p className="text-2xl font-bold text-indigo-600 mt-3">${p.price.toFixed(2)}</p>
                <div className="flex gap-2 mt-4">
                  <button onClick={() => addItem(p)}
                    className="flex-1 py-2 border border-indigo-600 text-indigo-600 rounded-lg hover:bg-indigo-50 text-sm">
                    Add to Cart
                  </button>
                  <button onClick={() => handleBuyNow(p)} disabled={buying === p.id}
                    className="flex-1 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 text-sm">
                    {buying === p.id ? "Processing..." : "Buy Now"}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Ops panel — framed as production traffic simulation, not "inject failure" */}
        <details className="mt-12 p-4 bg-gray-100 rounded-lg border border-gray-200">
          <summary className="cursor-pointer text-sm text-gray-500 font-medium">Ops Tools (simulate production traffic)</summary>
          <div className="mt-3 flex gap-3 flex-wrap">
            <button onClick={async () => { await runLoadGenerator(); alert("Traffic burst simulated — payment pool under load"); }}
              className="px-4 py-2 bg-gray-700 text-white text-sm rounded-lg hover:bg-gray-800">
              Simulate Traffic Burst
            </button>
            <button onClick={async () => { await toggleRoute(); await loadProducts(); }}
              className="px-4 py-2 bg-gray-700 text-white text-sm rounded-lg hover:bg-gray-800">
              Toggle Deployment Config
            </button>
          </div>
        </details>
      </main>
    </div>
  );
}
