import React from "react";
import "./footer.css";

const LINKS = {
    "Shop": ["Electronics", "Phones & Tablets", "Computers", "Audio & Music", "Gaming", "Cameras", "Wearables"],
    "Customer Service": ["Help Center", "Track Your Order", "Returns & Refunds", "Buyer Protection", "Report a Problem"],
    "About ShopAI": ["About Us", "Press", "Careers", "Investor Relations", "ShopAI Blog", "Affiliates"],
    "Connect": ["Facebook", "Twitter / X", "Instagram", "YouTube", "LinkedIn"],
};

export default function Footer() {
    return (
        <footer className="footer">

            {/* ── Promo strip ── */}
            <div className="footer__strip">
                <div className="footer__strip-inner">
                    <span className="footer__strip-item">🚚 Free Shipping on $25+</span>
                    <span className="footer__strip-divider">|</span>
                    <span className="footer__strip-item">🔄 30-Day Easy Returns</span>
                    <span className="footer__strip-divider">|</span>
                    <span className="footer__strip-item">🛡️ Buyer Protection Guarantee</span>
                    <span className="footer__strip-divider">|</span>
                    <span className="footer__strip-item">💳 100% Secure Payment</span>
                </div>
            </div>

            {/* ── Main footer ── */}
            <div className="footer__main">
                <div className="footer__brand-col">
                    <a href="/" className="footer__logo">
                        <span className="footer__logo-icon">🛒</span>
                        <span className="footer__logo-reco">Shop</span><span className="footer__logo-ai">AI</span>
                    </a>
                    <p className="footer__brand-desc">
                        AI-powered product recommendations using collaborative filtering and content-based filtering on real Amazon Electronics data.
                    </p>
                    <div className="footer__tech-tags">
                        <span className="footer__tag">Flask API</span>
                        <span className="footer__tag">React</span>
                        <span className="footer__tag">NumPy</span>
                        <span className="footer__tag">scikit-learn</span>
                    </div>
                    <div className="footer__social">
                        {["GitHub", "LinkedIn", "Twitter"].map(s => (
                            <a key={s} href="#recommend" className="footer__social-btn">{s[0]}</a>
                        ))}
                    </div>
                </div>

                {Object.entries(LINKS).map(([heading, links]) => (
                    <div key={heading} className="footer__col">
                        <h4 className="footer__col-heading">{heading}</h4>
                        <ul className="footer__col-list">
                            {links.map(link => (
                                <li key={link}><a href="#recommend" className="footer__col-link">{link}</a></li>
                            ))}
                        </ul>
                    </div>
                ))}
            </div>

            {/* ── Bottom bar ── */}
            <div className="footer__bottom">
                <div className="footer__bottom-inner">
                    <p className="footer__copy">
                        © 2024 ShopAI. Academic project — E-Commerce Recommendation System.
                        Built with <span className="footer__heart">♥</span> using Collaborative &amp; Content-Based Filtering.
                    </p>
                    <div className="footer__bottom-links">
                        <a href="#recommend" className="footer__bottom-link">Privacy Policy</a>
                        <a href="#recommend" className="footer__bottom-link">Terms of Service</a>
                        <a href="#recommend" className="footer__bottom-link">Cookie Policy</a>
                    </div>
                </div>
            </div>

        </footer>
    );
}
