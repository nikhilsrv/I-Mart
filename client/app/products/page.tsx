"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

interface Product {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  price: number;
  compare_price: number | null;
  sku: string | null;
  stock_quantity: number;
  is_active: boolean;
  image_url: string | null;
  category_id: string;
  created_at: string;
  updated_at: string;
}

interface ProductListResponse {
  products: Product[];
  next_cursor: string | null;
  has_more: boolean;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const fetchProducts = useCallback(
    async (cursor?: string | null, reset = false) => {
      try {
        if (reset) {
          setIsLoading(true);
        } else {
          setIsLoadingMore(true);
        }
        setError(null);

        const params = new URLSearchParams();
        params.set("limit", "20");
        if (cursor) params.set("cursor", cursor);
        if (debouncedSearch) params.set("search", debouncedSearch);

        const response = await fetch(
          `${API_BASE_URL}/api/products?${params.toString()}`
        );

        if (!response.ok) {
          throw new Error("Failed to fetch products");
        }

        const data: ProductListResponse = await response.json();

        if (reset) {
          setProducts(data.products);
        } else {
          setProducts((prev) => [...prev, ...data.products]);
        }
        setNextCursor(data.next_cursor);
        setHasMore(data.has_more);
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setIsLoading(false);
        setIsLoadingMore(false);
      }
    },
    [debouncedSearch]
  );

  // Initial fetch and search changes
  useEffect(() => {
    fetchProducts(null, true);
  }, [fetchProducts]);

  const handleLoadMore = () => {
    if (nextCursor && !isLoadingMore) {
      fetchProducts(nextCursor, false);
    }
  };

  const calculateDiscount = (price: number, comparePrice: number | null) => {
    if (!comparePrice || comparePrice <= price) return null;
    return Math.round(((comparePrice - price) / comparePrice) * 100);
  };

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header Section */}
      <section className="bg-gradient-to-br from-blue-600 via-blue-700 to-purple-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
          <div className="text-center">
            <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
              Our Products
            </h1>
            <p className="text-lg text-blue-100 max-w-2xl mx-auto mb-8">
              Discover our wide selection of quality products at amazing prices
            </p>

            {/* Search Bar */}
            <div className="max-w-xl mx-auto">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search products..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 rounded-full text-gray-900 focus:outline-none focus:ring-4 focus:ring-white/30"
                />
                <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              </div>
            </div>
          </div>
        </div>
        {/* Wave decoration */}
        <div className="relative h-8">
          <svg
            className="absolute bottom-0 w-full"
            viewBox="0 0 1440 48"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            preserveAspectRatio="none"
          >
            <path
              d="M0 48L60 42C120 36 240 24 360 18C480 12 600 12 720 15C840 18 960 24 1080 27C1200 30 1320 30 1380 30L1440 30V48H1380C1320 48 1200 48 1080 48C960 48 840 48 720 48C600 48 480 48 360 48C240 48 120 48 60 48H0Z"
              fill="#F9FAFB"
            />
          </svg>
        </div>
      </section>

      {/* Products Section */}
      <section className="py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Results count */}
          {!isLoading && (
            <div className="mb-6 flex items-center justify-between">
              <p className="text-gray-600">
                {products.length} product{products.length !== 1 ? "s" : ""}{" "}
                found
                {debouncedSearch && (
                  <span>
                    {" "}
                    for &quot;<strong>{debouncedSearch}</strong>&quot;
                  </span>
                )}
              </p>
            </div>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
              {[...Array(8)].map((_, i) => (
                <div
                  key={i}
                  className="bg-white rounded-2xl border border-gray-200 overflow-hidden animate-pulse"
                >
                  <div className="aspect-square bg-gray-200" />
                  <div className="p-4 space-y-3">
                    <div className="h-3 bg-gray-200 rounded w-1/3" />
                    <div className="h-4 bg-gray-200 rounded w-3/4" />
                    <div className="h-4 bg-gray-200 rounded w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="text-center py-12">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
                <ExclamationIcon className="w-8 h-8 text-red-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Failed to load products
              </h3>
              <p className="text-gray-500 mb-4">{error}</p>
              <button
                onClick={() => fetchProducts(null, true)}
                className="px-6 py-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors"
              >
                Try Again
              </button>
            </div>
          )}

          {/* Empty State */}
          {!isLoading && !error && products.length === 0 && (
            <div className="text-center py-12">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
                <PackageIcon className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                No products found
              </h3>
              <p className="text-gray-500">
                {debouncedSearch
                  ? "Try adjusting your search terms"
                  : "Check back later for new products"}
              </p>
            </div>
          )}

          {/* Products Grid */}
          {!isLoading && !error && products.length > 0 && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 md:gap-6">
                {products.map((product) => {
                  const discount = calculateDiscount(
                    product.price,
                    product.compare_price
                  );

                  return (
                    <Link
                      key={product.id}
                      href={`/products/${product.slug}`}
                      className="group bg-white rounded-2xl border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow"
                    >
                      <div className="relative aspect-square bg-gray-100 flex items-center justify-center">
                        {product.image_url ? (
                          <img
                            src={product.image_url}
                            alt={product.name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <PackageIcon className="w-16 h-16 text-gray-300" />
                        )}
                        {discount && (
                          <span className="absolute top-3 left-3 px-2 py-1 bg-red-500 text-white text-xs font-semibold rounded-full">
                            {discount}% OFF
                          </span>
                        )}
                        {product.stock_quantity === 0 && (
                          <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                            <span className="px-3 py-1 bg-white text-gray-900 text-sm font-semibold rounded-full">
                              Out of Stock
                            </span>
                          </div>
                        )}
                        <button
                          className="absolute top-3 right-3 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-md opacity-0 group-hover:opacity-100 transition-opacity"
                          onClick={(e) => {
                            e.preventDefault();
                            // Add to wishlist functionality
                          }}
                        >
                          <HeartIcon className="w-5 h-5 text-gray-400 hover:text-red-500 transition-colors" />
                        </button>
                      </div>
                      <div className="p-4">
                        <p className="text-sm text-gray-500 mb-1 truncate">
                          {product.sku || "Product"}
                        </p>
                        <h3 className="font-semibold text-gray-900 mb-2 truncate group-hover:text-blue-600 transition-colors">
                          {product.name}
                        </h3>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-blue-600">
                            ${Number(product.price).toFixed(2)}
                          </span>
                          {product.compare_price &&
                            product.compare_price > product.price && (
                              <span className="text-sm text-gray-400 line-through">
                                ${Number(product.compare_price).toFixed(2)}
                              </span>
                            )}
                        </div>
                        {product.stock_quantity > 0 &&
                          product.stock_quantity <= 5 && (
                            <p className="text-xs text-orange-600 mt-2">
                              Only {product.stock_quantity} left!
                            </p>
                          )}
                      </div>
                    </Link>
                  );
                })}
              </div>

              {/* Load More Button */}
              {hasMore && (
                <div className="mt-12 text-center">
                  <button
                    onClick={handleLoadMore}
                    disabled={isLoadingMore}
                    className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-full hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2"
                  >
                    {isLoadingMore ? (
                      <>
                        <LoadingSpinner className="w-5 h-5" />
                        Loading...
                      </>
                    ) : (
                      <>
                        Load More Products
                        <ChevronDownIcon className="w-5 h-5" />
                      </>
                    )}
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </section>
    </main>
  );
}

// Icon Components
function SearchIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
      />
    </svg>
  );
}

function HeartIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
      />
    </svg>
  );
}

function PackageIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={1.5}
        d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
      />
    </svg>
  );
}

function ExclamationIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
      />
    </svg>
  );
}

function ChevronDownIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M19 9l-7 7-7-7"
      />
    </svg>
  );
}

function LoadingSpinner({ className }: { className?: string }) {
  return (
    <svg className={`animate-spin ${className}`} fill="none" viewBox="0 0 24 24">
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}
