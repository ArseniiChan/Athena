"use client"

type Props = { src?: string; transcript?: string }

export default function AudioPlayer({ src, transcript }: Props) {
  if (!src) return null
  return (
    <div style={{ marginTop: "1.5rem" }}>
      <audio controls style={{ width: "100%" }} src={src} />
      {transcript && (
        <details style={{ marginTop: "1rem", background: "var(--athena-gray-50)", padding: "1rem", borderRadius: 8 }}>
          <summary style={{ cursor: "pointer", fontWeight: 600 }}>View generated script</summary>
          <pre style={{ whiteSpace: "pre-wrap", marginTop: ".75rem" }}>{transcript}</pre>
        </details>
      )}
    </div>
  )
}
