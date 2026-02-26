import React from "react";
import "./productcard.css";

const EMOJIS = ["🎧", "📱", "💻", "👟", "⌚", "🎮", "📷", "🛋️", "👕", "📚", "🎨", "🏋️"];
const CATS = ["Electronics", "Mobile", "Computers", "Footwear", "Wearables",
    "Gaming", "Cameras", "Home", "Apparel", "Books", "Design", "Fitness"];

function info(id) {
    const i = parseInt(id) % EMOJIS.length;
    return { emoji: EMOJIS[i], cat: CATS[i] };
}

export default function ProductCard({ productId, rank, style }) {
    const { emoji, cat } = info(productId);
    const score = Math.max(60, 100 - rank * 4 + Math.floor(Math.random() * 5));

    return (
        <div className="pcard" style={style}>
            <span className="pcard__rank">#{rank}</span>
            <div className="pcard__emoji">{emoji}</div>
            <div>
                <p className="pcard__name">Product {productId}</p>
                <p className="pcard__cat">{cat}</p>
            </div>
            <div>
                <div className="pcard__score-bar">
                    <div className="pcard__score-fill" style={{ width: `${score}%` }} />
                </div>
                <p className="pcard__score-label">{score}% match</p>
            </div>
        </div>
    );
}
