import React from "react";
import "./footer.css";

export default function Footer() {
    return (
        <footer className="footer">
            <div className="footer__inner">

                <div className="footer__brand">
                    <a href="/" className="footer__logo">
                        <span>🛒</span>
                        <span className="footer__logo-reco">Shop</span><span className="footer__logo-ai">AI</span>
                    </a>
                    <p className="footer__desc">
                        Smart product recommendations — built for shoppers who know what they want.
                    </p>
                    <div className="footer__tags">
                        {["Flask", "React", "NumPy", "scikit-learn", "SentenceTransformers"].map(t => (
                            <span key={t} className="footer__tag">{t}</span>
                        ))}
                    </div>
                </div>

                <div className="footer__links-grid">
                    <div className="footer__col">
                        <h4 className="footer__col-title">Shop</h4>
                        {["Electronics", "Phones", "Computers", "Audio", "Gaming"].map(l => (
                            <a key={l} href="#recommend" className="footer__link">{l}</a>
                        ))}
                    </div>
                    <div className="footer__col">
                        <h4 className="footer__col-title">Help</h4>
                        {["Returns", "Shipping", "FAQ", "Contact Us"].map(l => (
                            <a key={l} href="#recommend" className="footer__link">{l}</a>
                        ))}
                    </div>
                </div>

            </div>

            <div className="footer__bottom">
                <p>© 2025 ShopAI · Built with ♥</p>
                <div className="footer__bottom-links">
                    <a href="#recommend">Privacy</a>
                    <a href="#recommend">Terms</a>
                    <a href="#recommend">GitHub</a>
                </div>
            </div>
        </footer>
    );
}
