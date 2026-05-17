import { useState, useEffect } from "react";
import icon from "../../assets/logo.png";
import iconStats from "../../assets/icon-stats.svg";
import Button from "../Button/Button";
import s from "./Header.module.css";

interface UserLink {
  id: number;
  original: string;
  shortened: string;
  clicks: number;
}

type SortOrder = "none" | "desc" | "asc";

export default function Header() {
  const [activeModal, setActiveModal] = useState<
    "login" | "register" | "links" | null
  >(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [token, setToken] = useState<string | null>(() => {
    const storedToken = localStorage.getItem("token");
    if (
      storedToken &&
      storedToken !== "null" &&
      storedToken !== "undefined" &&
      storedToken !== ""
    ) {
      return storedToken;
    }
    return null;
  });

  const [userLinks, setUserLinks] = useState<UserLink[]>([]);
  const [sortOrder, setSortOrder] = useState<SortOrder>("none");

  const API_URL = "http://127.0.0.1:8000";

  useEffect(() => {
    if (!token) {
      localStorage.removeItem("token");
    }
  }, [token]);

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    try {
      const response = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData.toString(),
      });
      if (!response.ok) throw new Error("Invalid credentials");
      const data = await response.json();

      const tokenValue = data.access_token || data.token;
      if (tokenValue) {
        localStorage.setItem("token", tokenValue);
        setToken(tokenValue);
        setActiveModal(null);
        setUsername("");
        setPassword("");
      }
    } catch {
      alert("Login failed");
    }
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_URL}/registration`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ login: username, password }),
      });
      if (!response.ok) throw new Error("Registration failed");
      alert("Registration successful! Please log in.");
      setActiveModal("login");
    } catch {
      alert("Registration failed");
    }
  };

  const fetchUserLinks = async () => {
    if (!token) return;
    try {
      const response = await fetch(`${API_URL}/get/my`, {
        method: "GET",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Failed to fetch links");
      const data = await response.json();
      setUserLinks(data.links || []);
      setSortOrder("none");
    } catch (err) {
      console.error(err);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUserLinks([]);
    setActiveModal(null);
  };

  const toggleSort = () => {
    setSortOrder((prev) => {
      if (prev === "none") return "desc";
      if (prev === "desc") return "asc";
      return "none";
    });
  };

  const getSortedLinks = () => {
    const linksCopy = [...userLinks];
    if (sortOrder === "desc") {
      return linksCopy.sort((a, b) => b.clicks - a.clicks);
    }
    if (sortOrder === "asc") {
      return linksCopy.sort((a, b) => a.clicks - b.clicks);
    }
    return userLinks;
  };

  const sortedLinks = getSortedLinks();

  return (
    <>
      <header className={s.header}>
        <div className={s.container}>
          <img src={icon} alt="Cutto Logo" className={s.logo} />
          <nav className={s.nav}>
            <ul className={s.navList}>
              <li>
                <a
                  href="https://t.me/quantumlgm"
                  target="_blank"
                  rel="noopener noreferrer"
                  className={s.navLink}
                >
                  Contacts
                </a>
              </li>
              <li>
                <a
                  href={`${API_URL}/`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={s.navLink}
                >
                  Docs
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/quantumlgm"
                  target="_blank"
                  rel="noopener noreferrer"
                  className={s.navLink}
                >
                  Github
                </a>
              </li>
            </ul>
          </nav>
          <div className={s.authButtons}>
            {token ? (
              <>
                <Button
                  variant="ghost"
                  onClick={() => {
                    fetchUserLinks();
                    setActiveModal("links");
                  }}
                >
                  My Links
                </Button>
                <Button variant="primary" onClick={handleLogout}>
                  Log Out
                </Button>
              </>
            ) : (
              <>
                <Button variant="ghost" onClick={() => setActiveModal("login")}>
                  Log In
                </Button>
                <Button
                  variant="primary"
                  onClick={() => setActiveModal("register")}
                >
                  Sign Up
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      {activeModal === "login" && (
        <div className={s.modalOverlay}>
          <div className={s.modalContent}>
            <h2>Log In</h2>
            <form onSubmit={handleLoginSubmit}>
              <div className={s.formGroup}>
                <label>Username</label>
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
              <div className={s.formGroup}>
                <label>Password</label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              <div className={s.formActions}>
                <button type="submit" className={s.submitBtn}>
                  Submit
                </button>
                <button
                  type="button"
                  onClick={() => setActiveModal(null)}
                  className={s.cancelBtn}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {activeModal === "register" && (
        <div className={s.modalOverlay}>
          <div className={s.modalContent}>
            <h2>Sign Up</h2>
            <form onSubmit={handleRegisterSubmit}>
              <div className={s.formGroup}>
                <label>Username</label>
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
              <div className={s.formGroup}>
                <label>Password</label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              <div className={s.formActions}>
                <button type="submit" className={s.submitBtn}>
                  Submit
                </button>
                <button
                  type="button"
                  onClick={() => setActiveModal(null)}
                  className={s.cancelBtn}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {activeModal === "links" && (
        <div className={s.modalOverlay}>
          <div className={s.modalContent}>
            <div className={s.modalHeaderInline}>
              <h2>My Shortened Links</h2>
              <button
                className={`${s.sortButton} ${sortOrder !== "none" ? s.sortActive : ""}`}
                onClick={toggleSort}
                title="Sort by clicks"
              >
                <img src={iconStats} alt="Sort" className={s.sortIcon} />
                {sortOrder === "desc" && (
                  <span className={s.sortDirection}>▼</span>
                )}
                {sortOrder === "asc" && (
                  <span className={s.sortDirection}>▲</span>
                )}
              </button>
            </div>
            <div className={s.linksList}>
              {sortedLinks && sortedLinks.length > 0 ? (
                sortedLinks.map((link) => (
                  <div key={link.id} className={s.linkItem}>
                    <span className={s.originalUrl} title={link.original}>
                      {link.original}
                    </span>
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        marginTop: "6px",
                      }}
                    >
                      <a
                        href={`${API_URL}/${link.shortened}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={s.shortenedUrl}
                      >
                        {`${API_URL.replace(/^https?:\/\//, "")}/${link.shortened}`}
                      </a>
                      <span
                        style={{
                          fontSize: "12px",
                          color: "#94A3B8",
                          fontWeight: 500,
                        }}
                      >
                        Clicks: {link.clicks || 0}
                      </span>
                    </div>
                  </div>
                ))
              ) : (
                <div className={s.noLinks}>
                  You haven't shortened any links yet.
                </div>
              )}
            </div>
            <div className={s.formActions}>
              <button
                type="button"
                onClick={() => setActiveModal(null)}
                className={s.cancelBtn}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
