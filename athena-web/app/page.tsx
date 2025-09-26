"use client"

import { useEffect, useState } from "react"
import { Toaster, toast } from "sonner"
import FileUpload from "@/components/FileUpload"
import { Controls } from "@/components/Controls"
import AudioPlayer from "@/components/AudioPlayer"

export default function Home() {
  // ------------------------
  // Effects: smooth scroll, nav border, feature animations
  // ------------------------
  useEffect(() => {
    // Smooth scrolling (ignore href="#")
    const anchors = document.querySelectorAll<HTMLAnchorElement>(
      'a[href^="#"]:not([href="#"])'
    )

    const onClick = (e: Event) => {
      e.preventDefault()
      const href =
        (e.currentTarget as HTMLAnchorElement).getAttribute("href") || ""
      if (!href || href === "#") return
      const id = href.slice(1)
      const target = document.getElementById(id)
      if (target) target.scrollIntoView({ behavior: "smooth", block: "start" })
    }

    // Scroll effects (nav border)
    const onScroll = () => {
      const nav = document.querySelector("nav") as HTMLElement | null
      if (!nav) return
      const currentScroll = window.pageYOffset
      nav.style.borderBottom =
        currentScroll > 100
          ? "1px solid var(--athena-gray-200)"
          : "1px solid transparent"
    }

    // Intersection Observer for feature animations
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            (entry.target as HTMLElement).style.animationPlayState = "running"
          }
        })
      },
      { threshold: 0.1, rootMargin: "0px 0px -50px 0px" }
    )

    const features = Array.from(
      document.querySelectorAll<HTMLElement>(".feature")
    )
    features.forEach((el) => {
      el.style.animationPlayState = "paused"
      observer.observe(el)
    })

    // attach listeners
    anchors.forEach((a) => a.addEventListener("click", onClick))
    window.addEventListener("scroll", onScroll)

    // cleanup
    return () => {
      anchors.forEach((a) => a.removeEventListener("click", onClick))
      window.removeEventListener("scroll", onScroll)
      observer.disconnect()
    }
  }, [])

  // ------------------------
  // Upload + controls state
  // ------------------------
  const [file, setFile] = useState<File | null>(null)
  const [style, setStyle] = useState("conversational")
  const [speed, setSpeed] = useState(1.0)
  const [loading, setLoading] = useState(false)
  const [audioUrl, setAudioUrl] = useState<string | undefined>()
  const [script, setScript] = useState<string | undefined>()

  // ------------------------
  // Handlers from your script
  // ------------------------
  const handleGetStarted = () => {
    document
      .querySelector(".demo-section")
      ?.scrollIntoView({ behavior: "smooth" })
  }
  const handleDemo = () => {
    document
      .querySelector(".demo-section")
      ?.scrollIntoView({ behavior: "smooth" })
  }

  // (kept for click demo on the card – optional now that we have real upload)
  const handleUploadClick = () => {
    const uploadArea = document.querySelector(".upload-area")
    if (!uploadArea) return
    uploadArea.innerHTML = `
      <div class="loading"><div></div><div></div><div></div></div>
      <div class="upload-text" style="margin-top: 1rem;">Processing document...</div>
    `
    setTimeout(() => {
      uploadArea.innerHTML = `
        <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
          stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
        <div class="upload-text">Podcast ready</div>
        <div class="upload-subtext">Click to play or download</div>
      `
    }, 3000)
  }

  // Generate → call /api/convert
  const onGenerate = async () => {
    if (!file) return toast.error("Please upload a PDF first.")
    setLoading(true)
    setAudioUrl(undefined)
    setScript(undefined)
    try {
      const fd = new FormData()
      fd.append("file", file)
      fd.append("style", style)
      fd.append("speed", String(speed))

      const res = await fetch("/api/convert", { method: "POST", body: fd })
      const json = await res.json()
      if (!res.ok) throw new Error(json?.error || "Failed to convert")

      setAudioUrl(json.audioUrl)
      setScript(json.script)
      toast.success("Your podcast is ready 🎧")
      document.querySelector(".cta")?.scrollIntoView({ behavior: "smooth" })
    } catch (err: any) {
      toast.error(err.message || "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main>
      <Toaster richColors position="top-right" />

      {/* NAV */}
      <nav>
        <div className="nav-container">
          <a href="#" className="logo">
            Athena
          </a>
          <div className="nav-links">
            <a href="#features" className="nav-link">
              Features
            </a>
            <a href="#process" className="nav-link">
              How it works
            </a>
            <a href="#technology" className="nav-link">
              Technology
            </a>
            <button
              className="nav-cta"
              onClick={() =>
                document
                  .querySelector(".demo-section")
                  ?.scrollIntoView({ behavior: "smooth" })
              }
            >
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* HERO */}
      <section className="hero">
        <div className="hero-content">
          <h1>Transform PDFs into personalized podcasts</h1>
          <p className="hero-subtitle">
            Athena uses advanced AI to understand your documents and create
            engaging audio content tailored to your learning style.
          </p>
          <div className="hero-buttons">
            <button className="btn btn-primary" onClick={handleGetStarted}>
              Upload your first PDF
            </button>
            <button className="btn btn-secondary" onClick={handleDemo}>
              View demo
            </button>
          </div>
        </div>
      </section>

      {/* DEMO (now with real upload/controls/generate/output) */}
      <section className="demo-section">
        <div className="demo-container">
          <div className="demo-frame">
            <div className="demo-window">
              <div className="demo-header">
                <div className="demo-dot" />
                <div className="demo-dot" />
                <div className="demo-dot" />
              </div>
              <div
                className="demo-content"
                style={{ gap: "1.5rem", width: "100%" }}
              >
                {/* Drag/click upload with PDF-only+size validation */}
                <FileUpload onValidFile={setFile} />

                {/* Style + Speed controls */}
                <div style={{ width: "100%", maxWidth: 600 }}>
                  <Controls
                    style={style}
                    onStyle={setStyle}
                    speed={speed}
                    onSpeed={setSpeed}
                  />
                </div>

                {/* Generate button */}
                <button
                  className="btn btn-primary"
                  onClick={onGenerate}
                  disabled={loading}
                >
                  {loading ? "Generating..." : "Generate Podcast"}
                </button>

                {/* Output */}
                <div style={{ width: "100%", maxWidth: 800 }}>
                  <AudioPlayer src={audioUrl} transcript={script} />
                </div>

                {/* Keep the original click demo (optional) */}
                <div
                  className="upload-area"
                  onClick={handleUploadClick}
                  style={{ display: "none" }}
                >
                  {/* Hidden now; left here in case you want to toggle back */}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="features" id="features">
        <div className="features-grid">
          {[
            [
              "01",
              "Intelligent Processing",
              "Our AI comprehends complex academic materials, extracting key concepts and structuring them into clear, engaging narratives perfect for audio learning.",
            ],
            [
              "02",
              "Adaptive Learning",
              "Choose from detailed explanations, quick summaries, or storytelling formats. Athena adapts to your preferred learning style and pace.",
            ],
            [
              "03",
              "Natural Speech",
              "Google's advanced Text-to-Speech technology creates human-like narration that's easy to listen to during extended study sessions.",
            ],
            [
              "04",
              "Instant Generation",
              "Upload any PDF and receive your personalized podcast in seconds. Study while commuting, exercising, or relaxing.",
            ],
            [
              "05",
              "Universal Compatibility",
              "From biology to literature, mathematics to history—Athena handles any academic content with precision and clarity.",
            ],
            [
              "06",
              "Download & Share",
              "Export your podcasts as MP3 files to listen offline. Share with study groups or save for future review sessions.",
            ],
          ].map(([num, title, desc], i) => (
            <div className="feature" style={{ ["--index" as any]: i }} key={i}>
              <div className="feature-number">{num}</div>
              <h3 className="feature-title">{title}</h3>
              <p className="feature-description">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* PROCESS */}
      <section className="process" id="process">
        <div className="process-container">
          <h2 className="section-title">How it works</h2>
          <p className="section-subtitle">
            Three simple steps to transform your study materials
          </p>
          <div className="process-steps">
            {[
              ["1", "Upload", "Drop your PDF into Athena's secure upload area"],
              ["2", "Customize", "Select your preferred learning style and speed"],
              ["3", "Listen", "Stream or download your personalized podcast"],
            ].map(([num, title, desc]) => (
              <div className="process-step" key={num}>
                <div className="step-number">{num}</div>
                <h3 className="step-title">{title}</h3>
                <p className="step-description">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* TECH */}
      <section className="tech" id="technology">
        <h2 className="section-title">Powered by Google Cloud</h2>
        <p className="section-subtitle">
          Built on enterprise-grade AI infrastructure
        </p>
        <div className="tech-grid">
          {[
            "Vertex AI",
            "Gemini 1.5 Pro",
            "Document AI",
            "Cloud Text-to-Speech",
            "Cloud Run",
            "Firestore",
            "Cloud Storage",
          ].map((t) => (
            <div className="tech-item" key={t}>
              {t}
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="cta">
        <div className="cta-container">
          <h2 className="cta-title">Ready to transform your learning?</h2>
          <p className="cta-subtitle">
            Join thousands of students studying smarter with Athena
          </p>
          <button className="btn btn-primary" onClick={handleGetStarted}>
            Start now — it's free
          </button>
        </div>
      </section>

      {/* FOOTER */}
      <footer>
        <div className="footer-container">
          <div className="footer-text">
            © 2025 Athena. Built for Google Cloud Hackathon.
          </div>
          <div className="footer-links">
            <a href="#" className="footer-link">
              GitHub
            </a>
            <a href="#" className="footer-link">
              Documentation
            </a>
            <a href="#" className="footer-link">
              Contact
            </a>
          </div>
        </div>
      </footer>
    </main>
  )
}
