import React from "react";
import "./hero.css";

export default function HeroSection() {
    return (
        <section className="hero">
            <div className="hero__inner">
                <span className="hero__badge">🔥 Hot Deals Every Day</span>
                <h1 className="hero__title">
                    Shop Smarter, <span className="hero__accent">Save Bigger</span>
                </h1>
                <p className="hero__sub">
                    Millions of products at unbeatable prices. Free shipping, easy returns, and deals handpicked just for you every single day.
                </p>
                <div className="hero__cta-row">
                    <a href="#recommend" className="hero__btn hero__btn--primary">Get My Picks →</a>
                    <a href="#recommend" className="hero__btn hero__btn--secondary">Find Similar Items</a>
                </div>
                <div className="hero__props">
                    {[
                        { icon: "🚚", label: "Free Shipping on $25+" },
                        { icon: "🛡️", label: "Buyer Protection" },
                        { icon: "🔄", label: "30-Day Returns" },
                        { icon: "💳", label: "Secure Payment" },
                    ].map(p => (
                        <div key={p.label} className="hero__prop">
                            <span>{p.icon}</span> {p.label}
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
