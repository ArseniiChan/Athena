"use client"

type Props = {
  style: string
  onStyle: (v: string) => void
  speed: number
  onSpeed: (v: number) => void
}

export function Controls({ style, onStyle, speed, onSpeed }: Props) {
  return (
    <div style={{ display: "grid", gap: "1rem" }}>
      {/* Style selector */}
      <div>
        <label className="feature-number" style={{ display: "block", marginBottom: ".5rem" }}>Learning style</label>
        <div style={{ display: "flex", gap: ".5rem", flexWrap: "wrap" }}>
          {["conversational", "academic", "simplified"].map((opt) => (
            <button
              key={opt}
              type="button"
              onClick={() => onStyle(opt)}
              className="btn btn-secondary"
              style={{
                borderColor: style === opt ? "black" : "var(--athena-gray-300)",
                background: style === opt ? "var(--athena-gray-50)" : "white",
              }}
            >
              {opt[0].toUpperCase() + opt.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Speed slider */}
      <div>
        <label className="feature-number" style={{ display: "block", marginBottom: ".25rem" }}>
          Speed: {speed.toFixed(2)}×
        </label>
        <input
          type="range"
          min={0.8}
          max={1.3}
          step={0.05}
          value={speed}
          onChange={(e) => onSpeed(parseFloat(e.target.value))}
          style={{ width: "100%" }}
        />
        <div className="upload-subtext">0.8× to 1.3×</div>
      </div>
    </div>
  )
}
