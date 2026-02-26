import React from "react";
import "./hero.css";

export default function HeroSection() {
    return (
        <section className="hero" id="about">

            <div className="hero__badge">
                <span className="hero__dot" />
                AI-Powered &bull; Real-Time &bull; Personalized
            </div>

            <h1 className="hero__h1">
                <span className="hero__line hero__line--plain">Discover</span>
                <span className="hero__line hero__line--grad">Products You'll</span>
                <span className="hero__line hero__line--stroke">Love.</span>
            </h1>

            <p className="hero__sub">
                Our machine-learning engine analyzes real purchase patterns
                to surface hyper-personalized recommendations — uniquely crafted
                for every single user.
            </p>

            <div className="hero__actions">
                <a href="#recommend" className="hero__btn">
                    Get Recommendations
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M5 12h14" /><path d="M12 5l7 7-7 7" />
                    </svg>
                </a>
                <div className="hero__trust">
                    <div className="hero__faces">
                        {["🧑‍💻", "👩", "👨🏽", "🧑🏻", "👩🏾"].map((f, i) => (
                            <span key={i} className="hero__face">{f}</span>
                        ))}
                    </div>
                    <span className="hero__trust-text"><strong>1,200+ users</strong> trust us</span>
                </div>
            </div>

            <div className="hero__stats">
                <div className="hero__stat">
                    <span className="hero__stat-n">98%</span>
                    <span className="hero__stat-l">Accuracy</span>
                </div>
                <div className="hero__stat-sep" />
                <div className="hero__stat">
                    <span className="hero__stat-n">&lt;50ms</span>
                    <span className="hero__stat-l">Response</span>
                </div>
                <div className="hero__stat-sep" />
                <div className="hero__stat">
                    <span className="hero__stat-n">10K+</span>
                    <span className="hero__stat-l">Products</span>
                </div>
            </div>

            {/* Decorative rings */}
            <div className="hero__ring hero__ring--1" />
            <div className="hero__ring hero__ring--2" />
        </section>
    );
}
