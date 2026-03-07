import React, { useState, useEffect } from "react";
import axios from "axios";
import ProductCard from "./ProductCard";
import "./recommendform.css";

const API = "http://localhost:5000";

export default function RecommendForm() {
    const [userId, setUserId] = useState("");
    const [userList, setUserList] = useState([]);
    const [recs, setRecs] = useState([]);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const [done, setDone] = useState(false);
    const [usersLoading, setUsersLoading] = useState(true);

    // ── Fetch valid user IDs from backend on mount ───────────────────────────
    useEffect(() => {
        axios.get(`${API}/users`)
            .then(res => {
                setUserList(res.data.users || []);
                if (res.data.users && res.data.users.length > 0) {
                    setUserId(res.data.users[0]); // pre-select first user
                }
            })
            .catch(() => {
                setError("Cannot connect to backend. Make sure the server is running on port 5000.");
            })
            .finally(() => setUsersLoading(false));
    }, []);

    // ── Submit ───────────────────────────────────────────────────────────────
    const submit = async (e) => {
        e.preventDefault();
        setRecs([]); setError(""); setLoading(true); setDone(false);
        try {
            const res = await axios.post(`${API}/recommend`, { user_id: userId });
            setRecs(res.data.recommendations);
            setDone(true);
        } catch (err) {
            setError(
                err.response
                    ? err.response.data.error
                    : "Cannot connect to server. Make sure the backend is running."
            );
        } finally {
            setLoading(false);
        }
    };

    const reset = () => { setUserId(userList[0] || ""); setRecs([]); setError(""); setDone(false); };

    return (
        <div className="rf">
            {/* ── Form card ── */}
            <div className="rf__card">
                <div className="rf__hdr">
                    <div className="rf__icon">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" />
                        </svg>
                    </div>
                    <div>
                        <h2 className="rf__title">Discover Products</h2>
                        <p className="rf__sub">Select a User ID to discover personalized products</p>
                    </div>
                </div>

                <form className="rf__form" onSubmit={submit}>
                    <div className="rf__label-row">
                        <label className="rf__label" htmlFor="uid">User ID</label>
                        <div className="rf__wrap">
                            <span className="rf__ico">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                                    <circle cx="12" cy="7" r="4" />
                                </svg>
                            </span>

                            {usersLoading ? (
                                <div className="rf__input" style={{ display: "flex", alignItems: "center", color: "var(--rf-muted, #888)" }}>
                                    <span className="rf__spin" style={{ marginRight: 8 }} />
                                    Loading users…
                                </div>
                            ) : (
                                <select
                                    id="uid"
                                    className="rf__input"
                                    value={userId}
                                    onChange={e => setUserId(e.target.value)}
                                    required
                                    disabled={loading}
                                >
                                    {userList.map(uid => (
                                        <option key={uid} value={uid}>{uid}</option>
                                    ))}
                                </select>
                            )}
                        </div>
                    </div>

                    <button className={`rf__btn${loading ? " rf__btn--loading" : ""}`} type="submit" disabled={loading || usersLoading}>
                        {loading ? (
                            <><span className="rf__spin" />Analyzing…</>
                        ) : (
                            <>
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                                    <polygon points="5 3 19 12 5 21 5 3" />
                                </svg>
                                Discover
                            </>
                        )}
                    </button>
                </form>

                {error && (
                    <div className="rf__err">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                            <circle cx="12" cy="12" r="10" />
                            <line x1="12" y1="8" x2="12" y2="12" />
                            <line x1="12" y1="16" x2="12.01" y2="16" />
                        </svg>
                        {error}
                    </div>
                )}
            </div>

            {/* ── Results ── */}
            {done && recs.length > 0 && (
                <div className="rf__results">
                    <div className="rf__results-hdr">
                        <h3 className="rf__results-title">
                            Top {recs.length} picks for User&nbsp;
                            <span className="rf__results-uid">#{userId}</span>
                        </h3>
                        <button className="rf__reset" onClick={reset}>New Search</button>
                    </div>
                    <div className="rf__grid">
                        {recs.map((product, i) => (
                            <ProductCard
                                key={product.asin}
                                product={product}
                                style={{ animationDelay: `${i * 0.07}s` }}
                            />
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}