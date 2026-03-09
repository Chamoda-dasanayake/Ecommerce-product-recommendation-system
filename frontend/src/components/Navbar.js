import React, { useState, useEffect } from "react";
import "./navbar.css";

export default function Navbar({ onSearch }) {
    const [solid, setSolid] = useState(false);
    const [query, setQuery] = useState("");

    useEffect(() => {
        const fn = () => setSolid(window.scrollY > 10);
        window.addEventListener("scroll", fn, { passive: true });
        return () => window.removeEventListener("scroll", fn);
    }, []);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim()) onSearch(query.trim());
    };

    return (
        <header className={`navbar ${solid ? "navbar--solid" : ""}`}>
            <div className="navbar__inner">

                <a href="/" className="navbar__logo">
                    <span className="navbar__logo-icon">🛒</span>
                    <span className="navbar__logo-text">
                        <span className="navbar__logo-reco">Shop</span><span className="navbar__logo-ai">AI</span>
                    </span>
                </a>

                <form className="navbar__search" onSubmit={handleSubmit}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                        <circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" />
                    </svg>
                    <input
                        type="text"
                        className="navbar__search-input"
                        placeholder="Search products… e.g. wireless gaming headphones"
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                    />
                    <button className="navbar__search-btn" type="submit">Search</button>
                </form>

                <div className="navbar__actions">
                    <a href="#recommend" className="navbar__action">Deals</a>
                    <a href="#recommend" className="navbar__action">Sign In</a>
                    <button className="navbar__cart" aria-label="Cart">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <circle cx="9" cy="21" r="1" /><circle cx="20" cy="21" r="1" />
                            <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
                        </svg>
                        <span className="navbar__cart-badge">0</span>
                    </button>
                </div>

            </div>

            <div className="navbar__cats">
                <div className="navbar__cats-inner">
                    {["All", "Electronics", "Phones", "Computers", "Audio", "Cameras", "Gaming", "Wearables", "Smart Home"].map(cat => (
                        <a key={cat} href="#recommend" className="navbar__cat">{cat}</a>
                    ))}
                </div>
            </div>
        </header>
    );
}
