import React from "react";
import "./footer.css";

export default function Footer() {
    return (
        <footer className="footer">
            <div className="footer__inner">

                {/* Brand */}
                <div className="footer__brand">
                    <a href="/" className="footer__logo">
                        <span>🛒</span>
                        <span className="footer__logo-reco">Shop</span><span className="footer__logo-ai">AI</span>
                    </a>
                    <p className="footer__desc">
                        AI recommendation engine built on real Amazon Electronics data using Collaborative Filtering &amp; Content-Based Filtering.
                    </p>
                    <div className="footer__tags">
                        {["Flask", "React", "NumPy", "scikit-learn", "Pandas"].map(t => (
                            <span key={t} className="footer__tag">{t}</span>
                        ))}
                    </div>
                </div>

                {/* Links */}
                <div className="footer__links-grid">
                    <div className="footer__col">
                        <h4 className="footer__col-title">Shop</h4>
                        {["Electronics", "Phones", "Computers", "Audio", "Gaming"].map(l => (
                            <a key={l} href="#recommend" className="footer__link">{l}</a>
                        ))}
                    </div>
                    <div className="footer__col">
                        <h4 className="footer__col-title">Help</h4>
                        {["Contact Us", "Returns", "Shipping", "FAQ", "Buyer Protection"].map(l => (
                            <a key={l} href="#recommend" className="footer__link">{l}</a>
                        ))}
                    </div>
                </div>

            </div>

            {/* Bottom */}
            <div className="footer__bottom">
                <p>© 2024 ShopAI — Academic Project · Built with ♥</p>
                <div className="footer__bottom-links">
                    <a href="#recommend">Privacy</a>
                    <a href="#recommend">Terms</a>
                    <a href="#recommend">GitHub</a>
                </div>
            </div>
        </footer>
    );
}
