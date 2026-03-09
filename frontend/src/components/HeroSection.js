import React from "react";
import "./hero.css";

const VALUE_PROPS = [
    { icon: "🚚", title: "Free Shipping", desc: "On orders over $25" },
    { icon: "🛡️", title: "Buyer Protection", desc: "Money-back guarantee" },
    { icon: "🔄", title: "Easy Returns", desc: "30-day return policy" },
    { icon: "💳", title: "Secure Payment", desc: "Encrypted & safe" },
];

export default function HeroSection() {
    return (
        <section className="hero">

            {/* ── Main Banner ── */}
            <div className="hero__banner">
                <div className="hero__banner-content">
                    <div className="hero__badge">✨ AI-Powered Recommendations</div>
                    <h1 className="hero__title">
                        Discover Products<br />
                        <span className="hero__title-accent">Tailored Just For You</span>
                    </h1>
                    <p className="hero__subtitle">
                        Our smart engine analyses millions of real user purchases to surface
                        the products you'll actually love — personalised by <strong>collaborative filtering</strong> and
                        refined by <strong>content similarity</strong>.
                    </p>
                    <div className="hero__cta-row">
                        <a href="#recommend" className="hero__cta-btn hero__cta-btn--primary">
                            🔍 Get My Recommendations
                        </a>
                        <a href="#recommend" className="hero__cta-btn hero__cta-btn--secondary">
                            Find Similar Items →
                        </a>
                    </div>
                    <div className="hero__stats">
                        <div className="hero__stat">
                            <span className="hero__stat-num">50K+</span>
                            <span className="hero__stat-label">Products Analysed</span>
                        </div>
                        <div className="hero__stat-divider" />
                        <div className="hero__stat">
                            <span className="hero__stat-num">2</span>
                            <span className="hero__stat-label">AI Algorithms</span>
                        </div>
                        <div className="hero__stat-divider" />
                        <div className="hero__stat">
                            <span className="hero__stat-num">99%</span>
                            <span className="hero__stat-label">Satisfaction Rate</span>
                        </div>
                    </div>
                </div>

                <div className="hero__visual">
                    <div className="hero__visual-card hero__visual-card--main">
                        <div className="hero__visual-emoji">🎧</div>
                        <div className="hero__visual-info">
                            <p className="hero__visual-name">Sony Elite Headphones</p>
                            <p className="hero__visual-price">$129 <span className="hero__visual-badge">97% match</span></p>
                        </div>
                    </div>
                    <div className="hero__visual-card hero__visual-card--sm hero__visual-card--top">
                        <div className="hero__visual-emoji-sm">💻</div>
                        <p className="hero__visual-name-sm">Dell Nova Laptop</p>
                        <p className="hero__visual-price-sm">$899</p>
                    </div>
                    <div className="hero__visual-card hero__visual-card--sm hero__visual-card--bot">
                        <div className="hero__visual-emoji-sm">⌚</div>
                        <p className="hero__visual-name-sm">Samsung Smart Watch</p>
                        <p className="hero__visual-price-sm">$249</p>
                    </div>
                    <div className="hero__ai-badge">
                        <span>🤖</span> AI Match
                    </div>
                </div>
            </div>

            {/* ── Value Props ── */}
            <div className="hero__props">
                {VALUE_PROPS.map(p => (
                    <div key={p.title} className="hero__prop">
                        <span className="hero__prop-icon">{p.icon}</span>
                        <div>
                            <p className="hero__prop-title">{p.title}</p>
                            <p className="hero__prop-desc">{p.desc}</p>
                        </div>
                    </div>
                ))}
            </div>

        </section>
    );
}
