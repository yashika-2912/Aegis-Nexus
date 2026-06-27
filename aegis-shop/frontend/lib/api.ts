const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Product {
  id: string;
  name: string;
  price: number;
  description: string;
  image: string;
}

export interface CartItem extends Product {
  quantity: number;
}

export async function login(email: string, password: string) {
  const res = await fetch(`${API}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Login failed");
  return res.json();
}

export async function getProducts(): Promise<Product[]> {
  const res = await fetch(`${API}/products`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to load products (${res.status})`);
  const data = await res.json();
  return data.products;
}

export async function buyNow(item: {
  product_id: string;
  product_name: string;
  price: number;
  quantity: number;
  user_email: string;
}) {
  const res = await fetch(`${API}/checkout/buy-now`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(item),
  });
  const data = await res.json().catch(() => ({ detail: res.statusText }));
  if (!res.ok) throw new Error(data.detail || `Checkout failed (${res.status})`);
  return data;
}

export async function runLoadGenerator() {
  const res = await fetch(`${API}/demo/load-generator`, { method: "POST" });
  return res.json();
}

export async function toggleRoute() {
  const res = await fetch(`${API}/demo/toggle-route`, { method: "POST" });
  return res.json();
}
