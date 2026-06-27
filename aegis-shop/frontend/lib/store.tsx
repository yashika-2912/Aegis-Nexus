"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { CartItem, Product } from "@/lib/api";

interface AuthCtx {
  email: string | null;
  name: string | null;
  token: string | null;
  login: (token: string, email: string, name: string) => void;
  logout: () => void;
}

interface CartCtx {
  items: CartItem[];
  addItem: (p: Product) => void;
  removeItem: (id: string) => void;
  clear: () => void;
  total: number;
}

const AuthContext = createContext<AuthCtx | null>(null);
const CartContext = createContext<CartCtx | null>(null);

export function Providers({ children }: { children: ReactNode }) {
  const [email, setEmail] = useState<string | null>(null);
  const [name, setName] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [items, setItems] = useState<CartItem[]>([]);

  useEffect(() => {
    const saved = localStorage.getItem("aegis-auth");
    if (saved) {
      const d = JSON.parse(saved);
      setEmail(d.email); setName(d.name); setToken(d.token);
    }
    const cart = localStorage.getItem("aegis-cart");
    if (cart) setItems(JSON.parse(cart));
  }, []);

  const authLogin = (t: string, e: string, n: string) => {
    setToken(t); setEmail(e); setName(n);
    localStorage.setItem("aegis-auth", JSON.stringify({ token: t, email: e, name: n }));
  };

  const logout = () => {
    setToken(null); setEmail(null); setName(null);
    localStorage.removeItem("aegis-auth");
  };

  const addItem = (p: Product) => {
    setItems(prev => {
      const existing = prev.find(i => i.id === p.id);
      const next = existing
        ? prev.map(i => i.id === p.id ? { ...i, quantity: i.quantity + 1 } : i)
        : [...prev, { ...p, quantity: 1 }];
      localStorage.setItem("aegis-cart", JSON.stringify(next));
      return next;
    });
  };

  const removeItem = (id: string) => {
    setItems(prev => {
      const next = prev.filter(i => i.id !== id);
      localStorage.setItem("aegis-cart", JSON.stringify(next));
      return next;
    });
  };

  const clear = () => { setItems([]); localStorage.removeItem("aegis-cart"); };
  const total = items.reduce((s, i) => s + i.price * i.quantity, 0);

  return (
    <AuthContext.Provider value={{ email, name, token, login: authLogin, logout }}>
      <CartContext.Provider value={{ items, addItem, removeItem, clear, total }}>
        {children}
      </CartContext.Provider>
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext)!;
export const useCart = () => useContext(CartContext)!;
