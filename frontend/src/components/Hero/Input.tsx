import { useState, useEffect } from "react";
import iconLink from "../../assets/icon-link.svg";
import Button from "../Button/Button";
import s from "./Input.module.css";

interface Props {
  placeholder?: string;
}

export default function Input({ placeholder = "Paste your long URL" }: Props) {
  const [url, setUrl] = useState("");
  const [shortenedCode, setShortenedCode] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showOptions, setShowOptions] = useState(false);
  const [customText, setCustomText] = useState("");
  const [expireTime, setExpireTime] = useState("");

  const [qrBlobUrl, setQrBlobUrl] = useState<string | null>(null);
  const [isQrLoading, setIsQrLoading] = useState(false);
  const [fillColor, setFillColor] = useState("#D16B4B");
  const [backColor, setBackColor] = useState("#FFFFFF");
  const [gradientType, setGradientType] = useState<string>("none");
  const [gradientColor, setGradientColor] = useState("#1A1A1A");
  const [dotsStyle, setDotsStyle] = useState("square");
  const [eyeStyle, setEyeStyle] = useState("square");

  const API_URL = "http://127.0.0.1:8000";
  const fullShortLink = shortenedCode ? `${API_URL}/${shortenedCode}` : "";

  useEffect(() => {
    if (isModalOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isModalOpen]);

  const handleShorten = async () => {
    if (!url) {
      alert("Please enter a link!");
      return;
    }

    setIsLoading(true);
    try {
      const token = localStorage.getItem("token");
      const bodyData = {
        url: url,
        text: customText.trim() || null,
        time: expireTime ? Number(expireTime) : null,
      };

      const response = await fetch(`${API_URL}/create`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(bodyData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error while shortening link");
      }

      const data = await response.json();
      setShortenedCode(data.shortened);
      setIsModalOpen(true);
    } catch (err: any) {
      alert(err.message || "An unexpected error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  const generateQrCode = async () => {
    if (!fullShortLink) return;
    setIsQrLoading(true);

    try {
      const qrPayload = {
        url: fullShortLink,
        fill_color: fillColor,
        back_color: backColor,
        gradient_type: gradientType === "none" ? null : gradientType,
        gradient_color: gradientType === "none" ? null : gradientColor,
        dots_style: dotsStyle,
        eye_style: eyeStyle,
        border_style: "square",
      };

      const response = await fetch(`${API_URL}/qr/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(qrPayload),
      });

      if (!response.ok) throw new Error("Failed to generate QR code");

      const blob = await response.blob();
      if (qrBlobUrl) URL.revokeObjectURL(qrBlobUrl);
      setQrBlobUrl(URL.createObjectURL(blob));
    } catch (error) {
      console.error(error);
    } finally {
      setIsQrLoading(false);
    }
  };

  useEffect(() => {
    if (isModalOpen && fullShortLink) {
      const delayDebounce = setTimeout(() => {
        generateQrCode();
      }, 400);
      return () => clearTimeout(delayDebounce);
    }
  }, [
    fillColor,
    backColor,
    gradientType,
    gradientColor,
    dotsStyle,
    eyeStyle,
    isModalOpen,
  ]);

  return (
    <div className={s.container}>
      <div className={s.wrapper}>
        <img src={iconLink} alt="Link icon" className={s.icon} />
        <input
          type="text"
          placeholder={placeholder}
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className={s.input}
        />
        <Button variant="primary" onClick={handleShorten} disabled={isLoading}>
          {isLoading ? "Shortening..." : "Shorten URL"}
        </Button>
      </div>

      <button
        onClick={() => setShowOptions(!showOptions)}
        className={s.optionsToggle}
      >
        {showOptions ? "▾ Hide advanced options" : "▸ Show advanced options"}
      </button>

      {showOptions && (
        <div className={s.optionsPanel}>
          <div className={s.optionField}>
            <label className={s.label}>Custom Alias (Optional)</label>
            <input
              type="text"
              placeholder="e.g. my-custom-link"
              value={customText}
              onChange={(e) => setCustomText(e.target.value)}
              className={s.subInput}
            />
          </div>
          <div className={s.optionField}>
            <label className={s.label}>Link Expiration</label>
            <select
              value={expireTime}
              onChange={(e) => setExpireTime(e.target.value)}
              className={s.select}
            >
              <option value="">Never (Permanent)</option>
              <option value="1">1 Hour</option>
              <option value="24">1 Day</option>
              <option value="168">7 Days</option>
              <option value="720">30 Days</option>
            </select>
          </div>
        </div>
      )}

      {isModalOpen && (
        <div className={s.modalOverlay}>
          <div className={s.modalContentLarge}>
            <h2>Link successfully created!</h2>
            <p className={s.description}>Your short link:</p>

            <div className={s.linkBox}>
              <input
                type="text"
                readOnly
                value={fullShortLink}
                className={s.modalInput}
              />
              <button
                onClick={() => {
                  navigator.clipboard.writeText(fullShortLink);
                  alert("Link copied to clipboard!");
                }}
                className={s.copyBtn}
              >
                Copy
              </button>
            </div>

            <div className={s.qrWorkspace}>
              <div className={s.qrPreviewSection}>
                <div className={s.qrFrame}>
                  {isQrLoading && (
                    <div className={s.qrSpinner}>Loading...</div>
                  )}
                  {qrBlobUrl ? (
                    <img
                      src={qrBlobUrl}
                      alt="Generated QR Code"
                      className={s.qrImage}
                    />
                  ) : (
                    <div className={s.qrPlaceholder}>Generating preview...</div>
                  )}
                </div>
                {qrBlobUrl && (
                  <a
                    href={qrBlobUrl}
                    download={`qr-${shortenedCode}.png`}
                    className={s.downloadBtn}
                  >
                    Download PNG
                  </a>
                )}
              </div>

              <div className={s.qrControlsSection}>
                <h3>QR Design Settings</h3>

                <div className={s.controlGroupRow}>
                  <div className={s.controlItem}>
                    <label>Pattern color</label>
                    <input
                      type="color"
                      value={fillColor}
                      onChange={(e) => setFillColor(e.target.value)}
                    />
                  </div>
                  <div className={s.controlItem}>
                    <label>Background color</label>
                    <input
                      type="color"
                      value={backColor}
                      onChange={(e) => setBackColor(e.target.value)}
                    />
                  </div>
                </div>

                <div className={s.controlItem}>
                  <label>Gradient type</label>
                  <select
                    value={gradientType}
                    onChange={(e) => setGradientType(e.target.value)}
                  >
                    <option value="none">No gradient (Solid)</option>
                    <option value="horizontal">Horizontal</option>
                    <option value="radial">Radial</option>
                  </select>
                </div>

                {gradientType !== "none" && (
                  <div className={s.controlItem}>
                    <label>Second gradient color</label>
                    <input
                      type="color"
                      value={gradientColor}
                      onChange={(e) => setGradientColor(e.target.value)}
                    />
                  </div>
                )}

                <div className={s.controlItem}>
                  <label>Dot style (Pattern)</label>
                  <select
                    value={dotsStyle}
                    onChange={(e) => setDotsStyle(e.target.value)}
                  >
                    <option value="square">Square (Default)</option>
                    <option value="rounded">Rounded</option>
                    <option value="gapped">Separated dots</option>
                    <option value="circle">Circles</option>
                  </select>
                </div>

                <div className={s.controlItem}>
                  <label>Eye style</label>
                  <select
                    value={eyeStyle}
                    onChange={(e) => setEyeStyle(e.target.value)}
                  >
                    <option value="square">Square</option>
                    <option value="rounded">Rounded</option>
                  </select>
                </div>
              </div>
            </div>

            <button
              onClick={() => setIsModalOpen(false)}
              className={s.closeBtn}
            >
              Close editor
            </button>
          </div>
        </div>
      )}
    </div>
  );
}