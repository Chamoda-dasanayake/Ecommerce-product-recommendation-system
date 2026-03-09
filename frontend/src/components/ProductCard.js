import React, { useState } from "react";
import "./productcard.css";

const TYPE_IMAGE = {
    "Headphones": "/images/headphones.png",
    "Smart Speaker": "/images/smart_speaker.png",
    "Bluetooth Earbuds": "/images/earbuds.png",
    "Smartphone": "/images/smartphone.png",
    "Phone Case": "/images/phone_case.png",
    "Screen Protector": "/images/phone_case.png",   // close enough
    "Laptop": "/images/laptop.png",
    "Mechanical Keyboard": "/images/mechanical_keyboard.png",
    "Wireless Mouse": "/images/wireless_mouse.png",
    "USB-C Hub": "/images/usb_cable.png",    // similar accessory
    "Smart Watch": "/images/smartwatch.png",
    "Fitness Tracker": "/images/smartwatch.png",   // wearable
    "Gaming Controller": "/images/gaming_controller.png",
    "Gaming Headset": "/images/headphones.png",   // headphones style
    "DSLR Camera": "/images/dslr_camera.png",
    "Action Camera": "/images/action_camera.png",
    "Portable Charger": "/images/power_bank.png",
    "Cable Set": "/images/usb_cable.png",
    "Smart TV": "/images/smart_tv.png",
    "Streaming Stick": "/images/smart_tv.png",     // home entertainment
    "Tablet": "/images/tablet.png",
    "E-Reader": "/images/tablet.png",       // tablet style
    "Wireless Router": "/images/wifi_router.png",
    "Smart Home Hub": "/images/wifi_router.png",  // networking device
};

const TYPE_EMOJI = {
    "Headphones": "🎧", "Smart Speaker": "🔊", "Bluetooth Earbuds": "🎵",
    "Smartphone": "📱", "Phone Case": "📲", "Screen Protector": "📲",
    "Laptop": "💻", "Mechanical Keyboard": "⌨️", "Wireless Mouse": "🖱️",
    "USB-C Hub": "🔌", "Smart Watch": "⌚", "Fitness Tracker": "💪",
    "Gaming Controller": "🎮", "Gaming Headset": "🎮", "DSLR Camera": "📷",
    "Action Camera": "📷", "Portable Charger": "🔋", "Cable Set": "🔌",
    "Smart TV": "📺", "Streaming Stick": "📺", "Tablet": "📱",
    "E-Reader": "📚", "Wireless Router": "📡", "Smart Home Hub": "🏠",
};

export default function ProductCard({ product, style, onFindSimilar, mode }) {
    const { name, brand, category, price, rating, match_score, asin, product_type } = product;

    const [added, setAdded] = useState(false);
    const [imgOk, setImgOk] = useState(true);

    const fullStars = Math.floor(rating);
    const hasHalf = rating - fullStars >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalf ? 1 : 0);

    const imgSrc = TYPE_IMAGE[product_type];
    const fallback = TYPE_EMOJI[product_type] || "📦";

    const handleAddToCart = () => {
        setAdded(true);
        setTimeout(() => setAdded(false), 1600);
    };

    const scoreLabel = mode === "cbf" ? "Similarity" : "Match";

    return (
        <div className="pc" style={style}>

            {/* Product Image */}
            <div className="pc__img-wrap">
                {imgSrc && imgOk ? (
                    <img
                        src={imgSrc}
                        alt={product_type || name}
                        className="pc__img"
                        onError={() => setImgOk(false)}
                    />
                ) : (
                    <div className="pc__img-fallback">{fallback}</div>
                )}
                <span className="pc__cat-badge">{category}</span>
            </div>

            {/* Info */}
            <div className="pc__body">
                <p className="pc__brand">{brand}</p>
                <h3 className="pc__name" title={name}>{name}</h3>

                <div className="pc__stars">
                    {"★".repeat(fullStars)}{hasHalf ? "½" : ""}{"☆".repeat(emptyStars)}
                    <span className="pc__rating-val">{rating}</span>
                </div>

                <span className="pc__score-pill">{match_score}% {scoreLabel}</span>

                <div className="pc__price-row">
                    <span className="pc__price">${price}</span>
                    <span className="pc__orig">${Math.round(price * 1.2)}</span>
                </div>

                <div className="pc__actions">
                    <button
                        className={`pc__cart-btn ${added ? "pc__cart-btn--done" : ""}`}
                        onClick={handleAddToCart}
                    >
                        {added ? "✓ Added!" : "Add to Cart"}
                    </button>
                    {onFindSimilar && (
                        <button
                            className="pc__similar-btn"
                            onClick={() => onFindSimilar(asin, name)}
                            title="Find similar items"
                        >
                            🔍
                        </button>
                    )}
                </div>
            </div>

        </div>
    );
}
