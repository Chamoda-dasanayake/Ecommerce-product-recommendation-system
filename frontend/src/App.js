import React, { useState, useCallback } from "react";
import axios from "axios";
import "./App.css";
import Navbar from "./components/Navbar";
import HeroSection from "./components/HeroSection";
import RecommendForm from "./components/RecommendForm";
import SearchResults from "./components/SearchResults";
import Footer from "./components/Footer";

const API = "http://localhost:5000";

function App() {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState("");
  const [searchActive, setSearchActive] = useState(false);

  const handleSearch = useCallback(async (query) => {
    setSearchQuery(query);
    setSearchActive(true);
    setSearchLoading(true);
    setSearchResults([]);
    setSearchError("");
    window.scrollTo({ top: 0, behavior: "smooth" });
    try {
      const res = await axios.post(`${API}/search/semantic`, { query });
      setSearchResults(res.data.results || []);
    } catch (err) {
      setSearchError(
        err.response?.data?.error ||
        "Cannot connect to backend. Make sure the server is running."
      );
    } finally {
      setSearchLoading(false);
    }
  }, []);

  const handleClearSearch = () => {
    setSearchActive(false);
    setSearchQuery("");
    setSearchResults([]);
    setSearchError("");
  };

  return (
    <div className="app">
      <Navbar onSearch={handleSearch} />
      <main className="main">
        {searchActive ? (
          <SearchResults
            query={searchQuery}
            results={searchResults}
            loading={searchLoading}
            error={searchError}
            onClear={handleClearSearch}
            onFindSimilar={() => { }}
          />
        ) : (
          <>
            <HeroSection />
            <RecommendForm />
          </>
        )}
      </main>
      <Footer />
    </div>
  );
}

export default App;