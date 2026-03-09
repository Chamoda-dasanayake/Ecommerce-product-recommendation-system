import React from "react";
import "./hero.css";

export default function HeroSection() {
    return (
        <section className="hero">
            <div className="hero__inner">
                <span className="hero__badge">✨ AI-Powered</span>
                <h1 className="hero__title">
                    Discover Products <span className="hero__accent">Tailored For You</span>
                </h1>
                <p className="hero__sub">
                    Personalised recommendations powered by <strong>Collaborative Filtering</strong> and <strong>Content-Based Filtering</strong> — built on real Amazon Electronics data.
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
