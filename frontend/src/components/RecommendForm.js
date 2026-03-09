import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import ProductCard from "./ProductCard";
import "./recommendform.css";

const API = "http://localhost:5000";

export default function RecommendForm() {
    const [activeTab, setActiveTab] = useState("cf");

    const [userId, setUserId] = useState("");
    const [userList, setUserList] = useState([]);
    const [cfRecs, setCfRecs] = useState([]);
    const [cfError, setCfError] = useState("");
    const [cfLoading, setCfLoading] = useState(false);
    const [cfDone, setCfDone] = useState(false);
    const [usersLoading, setUsersLoading] = useState(true);

    const [asin, setAsin] = useState("");
    const [asinName, setAsinName] = useState("");
    const [cbfRecs, setCbfRecs] = useState([]);
    const [cbfError, setCbfError] = useState("");
    const [cbfLoading, setCbfLoading] = useState(false);
    const [cbfDone, setCbfDone] = useState(false);

    useEffect(() => {
        axios.get(`${API}/users`)
            .then(res => {
                setUserList(res.data.users || []);
                if (res.data.users?.length > 0) setUserId(res.data.users[0]);
            })
            .catch(() => setCfError("Cannot connect to backend. Make sure the server is running on port 5000."))
            .finally(() => setUsersLoading(false));
    }, []);

    const submitCF = async (e) => {
        e.preventDefault();
        setCfRecs([]); setCfError(""); setCfLoading(true); setCfDone(false);
        try {
            const res = await axios.post(`${API}/recommend`, { user_id: userId });
            setCfRecs(res.data.recommendations);
            setCfDone(true);
        } catch (err) {
            setCfError(err.response?.data?.error || "Cannot connect to server.");
        } finally {
            setCfLoading(false);
        }
    };

    const submitCBF = useCallback(async (targetAsin) => {
        const queryAsin = targetAsin || asin;
        if (!queryAsin.trim()) { setCbfError("Please enter a product ASIN."); return; }
        setCbfRecs([]); setCbfError(""); setCbfLoading(true); setCbfDone(false);
        try {
            const res = await axios.post(`${API}/recommend/content`, { asin: queryAsin.trim() });
            setCbfRecs(res.data.recommendations);
            setCbfDone(true);
        } catch (err) {
            setCbfError(err.response?.data?.error || "Cannot connect to server.");
        } finally {
            setCbfLoading(false);
        }
    }, [asin]);

    const handleFindSimilar = useCallback((productAsin, productName) => {
        setAsin(productAsin);
        setAsinName(productName);
        setActiveTab("cbf");
        setCbfDone(false); setCbfRecs([]); setCbfError("");
        setTimeout(() => submitCBF(productAsin), 100);
    }, [submitCBF]);

    const resetCF = () => { setUserId(userList[0] || ""); setCfRecs([]); setCfError(""); setCfDone(false); };
    const resetCBF = () => { setAsin(""); setAsinName(""); setCbfRecs([]); setCbfError(""); setCbfDone(false); };

    return (
        <section className="rf" id="recommend">
            <div className="rf__inner">

                {/* ── Section title ── */}
                <div className="rf__section-hdr">
                    <div className="rf__section-dot" />
                    <h2 className="rf__section-title">AI-Powered Recommendations</h2>
                    <p className="rf__section-sub">Two recommendation engines, one seamless experience</p>
                </div>

                <div className="rf__tabs">
                    <button
                        className={`rf__tab ${activeTab === "cf" ? "rf__tab--active" : ""}`}
                        onClick={() => setActiveTab("cf")}
                    >
                        <span className="rf__tab-icon">🧑</span>
                        <span>
                            <span className="rf__tab-title">For You</span>
                            <span className="rf__tab-desc">Collaborative Filtering</span>
                        </span>
                    </button>
                    <button
                        className={`rf__tab ${activeTab === "cbf" ? "rf__tab--active" : ""}`}
                        onClick={() => setActiveTab("cbf")}
                    >
                        <span className="rf__tab-icon">🔍</span>
                        <span>
                            <span className="rf__tab-title">Similar Items</span>
                            <span className="rf__tab-desc">Content-Based Filtering</span>
                        </span>
                    </button>
                </div>

                {activeTab === "cf" && (
                    <div className="rf__panel">
                        <div className="rf__panel-header">
                            <div>
                                <h3 className="rf__panel-title">Personalised For You</h3>
                                <p className="rf__panel-desc">
                                    Select a User ID to get personalised product recommendations based on users with similar purchase history.
                                </p>
                            </div>
                            <div className="rf__algo-badge rf__algo-badge--cf">Collaborative Filtering</div>
                        </div>

                        <form className="rf__form" onSubmit={submitCF}>
                            <div className="rf__field">
                                <label className="rf__label" htmlFor="uid">
                                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg>
                                    Customer User ID
                                </label>
                                {usersLoading ? (
                                    <div className="rf__loading-input">
                                        <span className="rf__spinner" />  Loading users…
                                    </div>
                                ) : (
                                    <select
                                        id="uid"
                                        className="rf__select"
                                        value={userId}
                                        onChange={e => setUserId(e.target.value)}
                                        disabled={cfLoading}
                                        required
                                    >
                                        {userList.map(uid => <option key={uid} value={uid}>{uid}</option>)}
                                    </select>
                                )}
                                <p className="rf__hint">
                                    💡 These are real User IDs from the Amazon Electronics ratings dataset.
                                </p>
                            </div>

                            <button className={`rf__submit-btn ${cfLoading ? "rf__submit-btn--loading" : ""}`} type="submit" disabled={cfLoading || usersLoading}>
                                {cfLoading
                                    ? <><span className="rf__spinner rf__spinner--white" /> Analysing purchase history…</>
                                    : <><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polygon points="5 3 19 12 5 21 5 3" /></svg> Get My Recommendations</>
                                }
                            </button>
                        </form>

                        {cfError && <div className="rf__error">⚠️ {cfError}</div>}

                        {cfDone && cfRecs.length > 0 && (
                            <div className="rf__results">
                                <div className="rf__results-header">
                                    <div>
                                        <h3 className="rf__results-title">
                                            Top {cfRecs.length} picks for
                                            <span className="rf__results-uid"> {userId}</span>
                                        </h3>
                                        <p className="rf__results-hint">Click &#34;🔍 Similar&#34; on any card to find content-based matches</p>
                                    </div>
                                    <button className="rf__reset-btn" onClick={resetCF}>New Search</button>
                                </div>
                                <div className="rf__grid">
                                    {cfRecs.map((product, i) => (
                                        <ProductCard
                                            key={product.asin}
                                            product={product}
                                            mode="cf"
                                            style={{ animationDelay: `${i * 0.05}s` }}
                                            onFindSimilar={handleFindSimilar}
                                        />
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* ════════════════ CBF PANEL ════════════════ */}
                {activeTab === "cbf" && (
                    <div className="rf__panel">
                        <div className="rf__panel-header">
                            <div>
                                <h3 className="rf__panel-title">Find Similar Items</h3>
                                <p className="rf__panel-desc">
                                    Enter a product ASIN to find items with similar features — same category, brand tier, and price range.
                                </p>
                            </div>
                            <div className="rf__algo-badge rf__algo-badge--cbf">Content-Based Filtering</div>
                        </div>

                        {asinName && (
                            <div className="rf__asin-context">
                                <span className="rf__asin-context-icon">🔗</span>
                                Showing results similar to: <strong>{asinName}</strong>
                                <button className="rf__asin-context-clear" onClick={resetCBF}>✕</button>
                            </div>
                        )}

                        <form className="rf__form" onSubmit={e => { e.preventDefault(); submitCBF(); }}>
                            <div className="rf__field">
                                <label className="rf__label" htmlFor="asin-input">
                                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" /></svg>
                                    Product ASIN
                                </label>
                                <input
                                    id="asin-input"
                                    type="text"
                                    className="rf__input"
                                    placeholder="e.g. B00004NKIQ  — get this from the 'For You' results"
                                    value={asin}
                                    onChange={e => { setAsin(e.target.value); setAsinName(""); }}
                                    disabled={cbfLoading}
                                />
                                <p className="rf__hint">
                                    💡 Use the <strong>&#34;🔍 Similar&#34;</strong> button on any &#34;For You&#34; card to auto-fill this field.
                                </p>
                            </div>

                            <button className={`rf__submit-btn rf__submit-btn--cbf ${cbfLoading ? "rf__submit-btn--loading" : ""}`} type="submit" disabled={cbfLoading}>
                                {cbfLoading
                                    ? <><span className="rf__spinner rf__spinner--white" /> Finding similar products…</>
                                    : <><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" /></svg> Find Similar Items</>
                                }
                            </button>
                        </form>

                        {cbfError && <div className="rf__error">⚠️ {cbfError}</div>}

                        {cbfDone && cbfRecs.length > 0 && (
                            <div className="rf__results">
                                <div className="rf__results-header">
                                    <div>
                                        <h3 className="rf__results-title">
                                            {cbfRecs.length} similar products found
                                            {asinName && <span className="rf__results-uid"> for {asinName}</span>}
                                        </h3>
                                        <p className="rf__results-hint">Ranked by feature similarity — category, brand tier, and price range</p>
                                    </div>
                                    <button className="rf__reset-btn" onClick={resetCBF}>New Search</button>
                                </div>
                                <div className="rf__grid">
                                    {cbfRecs.map((product, i) => (
                                        <ProductCard
                                            key={product.asin}
                                            product={product}
                                            mode="cbf"
                                            style={{ animationDelay: `${i * 0.05}s` }}
                                        />
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

            </div>
        </section>
    );
}