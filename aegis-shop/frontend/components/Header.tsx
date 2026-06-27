"use client";

import Link from "next/link";
import { useAuth, useCart } from "@/lib/store";

export default function Header() {
  const { email, name, logout } = useAuth();
  const { items } = useCart();

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold text-indigo-600">Aegis Shop</Link>
        <nav className="flex items-center gap-6 text-sm">
          <Link href="/" className="hover:text-indigo-600">Products</Link>
          <Link href="/cart" className="hover:text-indigo-600">
            Cart ({items.length})
          </Link>
          {email ? (
            <span className="flex items-center gap-3">
              <span className="text-gray-500">{name}</span>
              <button onClick={logout} className="text-red-500 hover:underline">Logout</button>
            </span>
          ) : (
            <Link href="/login" className="bg-indigo-600 text-white px-4 py-1.5 rounded-lg hover:bg-indigo-700">
              Login
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
