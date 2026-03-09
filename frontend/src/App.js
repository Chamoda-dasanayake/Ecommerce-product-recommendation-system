import React from "react";
import "./App.css";
import Navbar from "./components/Navbar";
import HeroSection from "./components/HeroSection";
import RecommendForm from "./components/RecommendForm";
import Footer from "./components/Footer";

function App() {
  return (
    <div className="app">
      <Navbar />
      <main className="main">
        <HeroSection />
        <RecommendForm />
      </main>
      <Footer />
    </div>
  );
}

export default App;