import React, { useState, useEffect } from "react";
import "./navbar.css";

const TICKERS = [
    "✦ AI-Powered Recommendations",
    "✦ Real-Time Results",
    "✦ Collaborative Filtering",
    "✦ Machine Learning Engine",
    "✦ Personalized Discovery",
    "✦ 10K+ Products",
];
// duplicate for seamless infinite scroll
const ALL = [...TICKERS, ...TICKERS];

export default function Navbar() {
    const [solid, setSolid] = useState(false);
    useEffect(() => {
        const fn = () => setSolid(window.scrollY > 50);
        window.addEventListener("scroll", fn, { passive: true });
        return () => window.removeEventListener("scroll", fn);
    }, []);

    return (
        <header className="hdr">
            {/* ─── Marquee ticker ─── */}
            <div className="ticker">
                <div className="ticker__track">
                    {ALL.map((t, i) => <span key={i} className="ticker__item">{t}</span>)}
                </div>
            </div>

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
                        <a href="#about" className="nav__link">Discover</a>
                        <a href="#recommend" className="nav__link">Explore</a>
                        <a href="#recommend" className="nav__link">How It Works</a>
                    </div>

                    {/* CTA */}
                    <a href="#recommend" className="nav__cta">
                        Try for free
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M5 12h14" /><path d="M12 5l7 7-7 7" />
                        </svg>
                    </a>
                </div>
            </nav>
        </header>
    );
}
