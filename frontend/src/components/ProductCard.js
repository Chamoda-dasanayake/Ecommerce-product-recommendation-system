import React from "react";
import "./productcard.css";

export default function ProductCard({ product, style }) {
    const { rank, name, brand, category, emoji, price, rating, match_score } = product;

    // Build star string
    const fullStars = Math.floor(rating);
    const half = rating - fullStars >= 0.5 ? "½" : "";
    const stars = "★".repeat(fullStars) + half;

    return (
        <div className="pcard" style={style}>
            <span className="pcard__rank">#{rank}</span>

            <div className="pcard__emoji">{emoji}</div>

            <div className="pcard__info">
                <p className="pcard__name">{name}</p>
                <p className="pcard__brand">{brand} &middot; {category}</p>
                <div className="pcard__meta">
                    <span className="pcard__price">${price}</span>
                    <span className="pcard__rating" title={`${rating} / 5`}>
                        {stars} <span className="pcard__rating-num">{rating}</span>
                    </span>
                </div>
            </div>

            <div className="pcard__score-wrap">
                <div className="pcard__score-bar">
                    <div
                        className="pcard__score-fill"
                        style={{ width: `${match_score}%` }}
                    />
                </div>
                <p className="pcard__score-label">{match_score}% match</p>
            </div>
        </div>
    );
}
