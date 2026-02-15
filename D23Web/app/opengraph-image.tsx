import { ImageResponse } from "next/og"

export const runtime = "edge"

export const alt = "D23 AI - Your Multilingual WhatsApp AI"
export const size = {
  width: 1200,
  height: 630,
}
export const contentType = "image/png"

export default async function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          height: "100%",
          width: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          backgroundColor: "#FAFAFA",
          backgroundImage: "linear-gradient(135deg, #FFFFFF 0%, #F5F5F5 100%)",
          position: "relative",
        }}
      >
        {/* Gradient blobs */}
        <div
          style={{
            position: "absolute",
            top: -100,
            left: -100,
            width: 400,
            height: 400,
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(139,92,246,0.1) 0%, transparent 70%)",
            filter: "blur(60px)",
          }}
        />
        <div
          style={{
            position: "absolute",
            bottom: -100,
            right: -100,
            width: 500,
            height: 500,
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(99,102,241,0.08) 0%, transparent 70%)",
            filter: "blur(80px)",
          }}
        />

        {/* Main content */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 10,
          }}
        >
          {/* Logo */}
          <div
            style={{
              display: "flex",
              alignItems: "baseline",
              marginBottom: 20,
            }}
          >
            <span
              style={{
                fontSize: 160,
                fontWeight: 700,
                color: "#171717",
                letterSpacing: "-0.02em",
              }}
            >
              D23
            </span>
            <span
              style={{
                fontSize: 160,
                fontWeight: 700,
                background: "linear-gradient(90deg, #7c3aed 0%, #6366f1 50%, #3b82f6 100%)",
                backgroundClip: "text",
                color: "transparent",
                letterSpacing: "-0.02em",
              }}
            >
              .AI
            </span>
          </div>

          {/* Tagline */}
          <p
            style={{
              fontSize: 40,
              color: "#525252",
              marginTop: 10,
              marginBottom: 16,
            }}
          >
            Your Multilingual WhatsApp AI
          </p>

          {/* Features */}
          <p
            style={{
              fontSize: 28,
              color: "#737373",
            }}
          >
            11+ Languages | Voice | Images | Games
          </p>
        </div>
      </div>
    ),
    {
      ...size,
    }
  )
}
