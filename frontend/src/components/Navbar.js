import React, { useState, useEffect } from "react";
import "./navbar.css";

const CATEGORIES = [
    { label: "All Categories", icon: "☰" },
    { label: "Electronics", icon: "⚡" },
    { label: "Phones", icon: "📱" },
    { label: "Computers", icon: "💻" },
    { label: "Audio", icon: "🎧" },
    { label: "Cameras", icon: "📷" },
    { label: "Gaming", icon: "🎮" },
    { label: "Wearables", icon: "⌚" },
    { label: "Smart Home", icon: "🏠" },
    { label: "Accessories", icon: "🔌" },
];

export default function Navbar() {
    const [solid, setSolid] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");
    const [activeCategory, setActiveCategory] = useState("All Categories");

    useEffect(() => {
        const fn = () => setSolid(window.scrollY > 10);
        window.addEventListener("scroll", fn, { passive: true });
        return () => window.removeEventListener("scroll", fn);
    }, []);

    return (
        <header className={`navbar ${solid ? "navbar--solid" : ""}`}>

            {/* ── Top utility bar ── */}
            <div className="navbar__topbar">
                <div className="navbar__topbar-inner">
                    <span className="navbar__topbar-text">🌍 Ship to: <strong>Sri Lanka</strong></span>
                    <div className="navbar__topbar-links">
                        <a href="#recommend" className="navbar__topbar-link">Daily Deals</a>
                        <a href="#recommend" className="navbar__topbar-link">Help &amp; Contact</a>
                        <a href="#recommend" className="navbar__topbar-link">Sign In</a>
                        <a href="#recommend" className="navbar__topbar-link">Register</a>
                    </div>
                </div>
            </div>

            {/* ── Main bar ── */}
            <div className="navbar__main">
                <div className="navbar__main-inner">

                    {/* Logo */}
                    <a href="/" className="navbar__logo">
                        <span className="navbar__logo-icon">🛒</span>
                        <span className="navbar__logo-text">
                            <span className="navbar__logo-reco">Shop</span><span className="navbar__logo-ai">AI</span>
                        </span>
                    </a>

                    {/* Search bar */}
                    <div className="navbar__search">
                        <select className="navbar__search-cat">
                            <option>All</option>
                            <option>Electronics</option>
                            <option>Phones</option>
                            <option>Computers</option>
                            <option>Audio</option>
                        </select>
                        <div className="navbar__search-divider" />
                        <input
                            type="text"
                            className="navbar__search-input"
                            placeholder="Search for products, brands and more..."
                            value={searchQuery}
                            onChange={e => setSearchQuery(e.target.value)}
                        />
                        <button className="navbar__search-btn" aria-label="Search">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                                <circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" />
                            </svg>
                        </button>
                    </div>

                    {/* Right icons */}
                    <div className="navbar__actions">
                        <button className="navbar__action-btn" aria-label="Wishlist">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                            </svg>
                            <span className="navbar__action-label">Wishlist</span>
                        </button>
                        <button className="navbar__action-btn navbar__cart-btn" aria-label="Cart">
                            <div className="navbar__cart-icon-wrap">
                                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <circle cx="9" cy="21" r="1" /><circle cx="20" cy="21" r="1" />
                                    <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
                                </svg>
                                <span className="navbar__cart-badge">0</span>
                            </div>
                            <span className="navbar__action-label">Cart</span>
                        </button>
                    </div>
                </div>
            </div>

            {/* ── Category bar ── */}
            <div className="navbar__catbar">
                <div className="navbar__catbar-inner">
                    {CATEGORIES.map(cat => (
                        <button
                            key={cat.label}
                            className={`navbar__cat-btn ${activeCategory === cat.label ? "navbar__cat-btn--active" : ""}`}
                            onClick={() => setActiveCategory(cat.label)}
                        >
                            <span className="navbar__cat-icon">{cat.icon}</span>
                            <span>{cat.label}</span>
                        </button>
                    ))}
                </div>
            </div>

        </header>
    );
}
