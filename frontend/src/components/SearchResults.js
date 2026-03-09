import React from "react";
import axios from "axios";
import ProductCard from "./ProductCard";
import "./searchresults.css";

const API = "http://localhost:5000";

export default function SearchResults({ query, results, loading, error, onClear, onFindSimilar }) {
    return (
        <section className="sr">
            <div className="sr__inner">

                <div className="sr__header">
                    <div className="sr__header-left">
                        <span className="sr__icon">🔎</span>
                        <div>
                            <h2 className="sr__title">
                                Results for <span className="sr__query">"{query}"</span>
                            </h2>
                            {!loading && !error && (
                                <p className="sr__count">{results.length} products found</p>
                            )}
                        </div>
                    </div>
                    <button className="sr__clear" onClick={onClear}>✕ Clear Search</button>
                </div>

                {loading && (
                    <div className="sr__loading">
                        <span className="sr__spinner" />
                        <span>Searching with AI…</span>
                    </div>
                )}

                {error && (
                    <div className="sr__error">⚠️ {error}</div>
                )}

                {!loading && !error && results.length > 0 && (
                    <div className="sr__grid">
                        {results.map((product, i) => (
                            <ProductCard
                                key={product.asin}
                                product={product}
                                mode="cbf"
                                style={{ animationDelay: `${i * 0.04}s` }}
                                onFindSimilar={onFindSimilar}
                            />
                        ))}
                    </div>
                )}

                {!loading && !error && results.length === 0 && (
                    <div className="sr__empty">
                        <span className="sr__empty-icon">🤷</span>
                        <p>No products found for "<strong>{query}</strong>"</p>
                        <p className="sr__empty-hint">Try different keywords like "wireless headphones" or "gaming mouse"</p>
                    </div>
                )}

            </div>
        </section>
    );
}
