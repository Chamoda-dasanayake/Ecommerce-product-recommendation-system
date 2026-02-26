import React from "react";
import "./App.css";
import Navbar from "./components/Navbar";
import HeroSection from "./components/HeroSection";
import RecommendForm from "./components/RecommendForm";

function App() {
  return (
    <div className="app">
      {/* Ambient glow orbs */}
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />

      <Navbar />

      <main className="main">
        <HeroSection />
        <div className="divider" />
        <section className="form-section">
          <div className="section-eyebrow">
            <div className="eyebrow-bar" />
            <span className="eyebrow-text">Personalized For You</span>
            <div className="eyebrow-bar" />
          </div>
          <RecommendForm />
        </section>
      </main>

      <footer className="footer">
        <p>
          Built with ❤️ by <span className="footer-brand">RecoAI</span>
          &nbsp;— powered by ML &amp; collaborative filtering
        </p>
      </footer>
    </div>
  );
}

export default App;