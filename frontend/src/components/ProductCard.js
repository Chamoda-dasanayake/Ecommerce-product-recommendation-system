import React, { useState } from "react";
import "./productcard.css";

export default function ProductCard({ product, style, onFindSimilar, mode }) {
    const { rank, name, brand, category, emoji, price, rating, match_score, asin } = product;

    const [wishlisted, setWishlisted] = useState(false);
    const [added, setAdded] = useState(false);

    const fullStars = Math.floor(rating);
    const hasHalf = rating - fullStars >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalf ? 1 : 0);

    const handleAddToCart = () => {
        setAdded(true);
        setTimeout(() => setAdded(false), 1800);
    };

    const scoreLabel = mode === "cbf" ? "Similarity" : "Match";
    const scoreColor = match_score >= 85 ? "var(--green)" : match_score >= 70 ? "var(--orange)" : "var(--grey)";

    return (
        <div className="pc" style={style}>

            {/* Rank badge */}
            <div className="pc__rank">#{rank}</div>

            {/* Wishlist toggle */}
            <button
                className={`pc__wish ${wishlisted ? "pc__wish--active" : ""}`}
                onClick={() => setWishlisted(w => !w)}
                aria-label="Wishlist"
            >
                {wishlisted ? "❤️" : "🤍"}
            </button>

            {/* Image area */}
            <div className="pc__img-wrap">
                <div className="pc__emoji">{emoji}</div>
                <span className="pc__cat-badge">{category}</span>
            </div>

            {/* Info */}
            <div className="pc__body">
                <p className="pc__brand">{brand}</p>
                <h3 className="pc__name">{name}</h3>

                {/* Stars */}
                <div className="pc__stars">
                    {"★".repeat(fullStars)}
                    {hasHalf ? "½" : ""}
                    {"☆".repeat(emptyStars)}
                    <span className="pc__rating-num">{rating}</span>
                </div>

                {/* Match score */}
                <div className="pc__score-row">
                    <div className="pc__score-bar">
                        <div className="pc__score-fill" style={{ width: `${match_score}%`, background: scoreColor }} />
                    </div>
                    <span className="pc__score-label" style={{ color: scoreColor }}>
                        {match_score}% {scoreLabel}
                    </span>
                </div>

                {/* Price */}
                <div className="pc__price-row">
                    <span className="pc__price">${price}</span>
                    <span className="pc__orig-price">${Math.round(price * 1.2)}</span>
                    <span className="pc__discount">-17%</span>
                </div>

                {/* CTA buttons */}
                <div className="pc__btns">
                    <button
                        className={`pc__cart-btn ${added ? "pc__cart-btn--added" : ""}`}
                        onClick={handleAddToCart}
                    >
                        {added ? "✓ Added!" : "🛒 Add to Cart"}
                    </button>
                    {onFindSimilar && (
                        <button
                            className="pc__similar-btn"
                            onClick={() => onFindSimilar(asin, name)}
                            title={`Find items similar to ${name}`}
                        >
                            🔍 Similar
                        </button>
                    )}
                </div>
            </div>

        </div>
    );
}
