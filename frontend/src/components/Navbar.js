import React, { useState, useEffect } from "react";
import "./navbar.css";


const NAV_LINKS = [
    { label: "Home", href: "/" },
    { label: "Discover", href: "#about" },
    { label: "Explore", href: "#recommend" },
    { label: "How It Works", href: "#how-it-works" },
    { label: "About", href: "#footer" },
];

export default function Navbar() {
    const [solid, setSolid] = useState(false);
    const [menuOpen, setMenuOpen] = useState(false);
    const [searchOpen, setSearchOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");

    useEffect(() => {
        const fn = () => setSolid(window.scrollY > 50);
        window.addEventListener("scroll", fn, { passive: true });
        return () => window.removeEventListener("scroll", fn);
    }, []);

    // Close mobile menu on outside click
    useEffect(() => {
        if (!menuOpen) return;
        const closeMenu = (e) => {
            if (!e.target.closest(".nav__mobile-menu") && !e.target.closest(".nav__hamburger")) {
                setMenuOpen(false);
            }
        };
        document.addEventListener("click", closeMenu);
        return () => document.removeEventListener("click", closeMenu);
    }, [menuOpen]);

    // Prevent body scroll when menu is open
    useEffect(() => {
        document.body.style.overflow = menuOpen ? "hidden" : "";
        return () => { document.body.style.overflow = ""; };
    }, [menuOpen]);

    return (
        <header className="hdr">
            {/* ─── Nav bar ─── */}
            <nav className={`nav ${solid ? "nav--solid" : ""}`}>
                <div className="nav__inner">

                    {/* Brand */}
                    <a href="/" className="brand">
                        <span className="brand__gem">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                                <polygon points="12,2 22,8.5 22,15.5 12,22 2,15.5 2,8.5" fill="url(#gp)" opacity=".9" />
                                <defs>
                                    <linearGradient id="gp" x1="0%" y1="0%" x2="100%" y2="100%">
                                        <stop offset="0%" stopColor="#7c3aed" />
                                        <stop offset="100%" stopColor="#22d3ee" />
                                    </linearGradient>
                                </defs>
                            </svg>
                        </span>
                        <span className="brand__text">
                            <span className="brand__reco">Reco</span><span className="brand__ai">AI</span>
                        </span>
                    </a>

                    {/* Center links inside floating capsule */}
                    <div className="nav__links">
                        {NAV_LINKS.map((link) => (
                            <a key={link.label} href={link.href} className="nav__link">
                                {link.label}
                            </a>
                        ))}
                    </div>

                    {/* Right actions */}
                    <div className="nav__actions">
                        {/* Search toggle */}
                        <button
                            className={`nav__icon-btn ${searchOpen ? "active" : ""}`}
                            onClick={() => setSearchOpen(!searchOpen)}
                            aria-label="Search"
                            title="Search"
                        >
                            {searchOpen ? (
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                                    <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
                                </svg>
                            ) : (
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
                                    <circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" />
                                </svg>
                            )}
                        </button>

                        {/* Wishlist */}
                        <button className="nav__icon-btn" aria-label="Wishlist" title="Wishlist">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
                            </svg>
                        </button>

                        {/* Cart */}
                        <button className="nav__icon-btn nav__cart-btn" aria-label="Cart" title="Cart">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                                <circle cx="9" cy="21" r="1" /><circle cx="20" cy="21" r="1" />
                                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
                            </svg>
                            <span className="nav__cart-badge">3</span>
                        </button>


                        {/* Hamburger */}
                        <button
                            className={`nav__hamburger ${menuOpen ? "open" : ""}`}
                            onClick={() => setMenuOpen(!menuOpen)}
                            aria-label="Menu"
                        >
                            <span /><span /><span />
                        </button>
                    </div>
                </div>

                {/* ─── Search bar (expandable) ─── */}
                <div className={`nav__search-bar ${searchOpen ? "nav__search-bar--open" : ""}`}>
                    <div className="nav__search-inner">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
                            <circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" />
                        </svg>
                        <input
                            type="text"
                            placeholder="Search products, categories…"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            autoFocus={searchOpen}
                        />
                        {searchQuery && (
                            <button onClick={() => setSearchQuery("")} className="nav__search-clear">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                                    <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
                                </svg>
                            </button>
                        )}
                    </div>
                </div>
            </nav>

            {/* ─── Mobile menu overlay ─── */}
            <div className={`nav__mobile-menu ${menuOpen ? "nav__mobile-menu--open" : ""}`}>
                <div className="nav__mobile-inner">
                    <div className="nav__mobile-links">
                        {NAV_LINKS.map((link) => (
                            <a
                                key={link.label}
                                href={link.href}
                                className="nav__mobile-link"
                                onClick={() => setMenuOpen(false)}
                            >
                                {link.label}
                            </a>
                        ))}
                    </div>
                </div>
            </div>

            {/* Backdrop */}
            {menuOpen && <div className="nav__backdrop" onClick={() => setMenuOpen(false)} />}
        </header>
    );
}
