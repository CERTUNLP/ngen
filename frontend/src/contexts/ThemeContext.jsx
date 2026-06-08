import PropTypes from "prop-types";
import React, { createContext, useCallback, useEffect, useState } from "react";

const STORAGE_KEY = "NGEN_THEME";

function getSystemTheme() {
  if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
    return "dark";
  }
  return "light";
}

function getStoredTheme() {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

function saveTheme(theme) {
  try {
    localStorage.setItem(STORAGE_KEY, theme);
  } catch {
    // localStorage not available
  }
}

function resolveTheme(stored) {
  if (stored === "dark" || stored === "light") return stored;
  return getSystemTheme();
}

function applyTheme(theme) {
  const resolved = resolveTheme(theme);
  document.documentElement.setAttribute("data-bs-theme", resolved);
}

const ThemeContext = createContext(undefined);

const ThemeProvider = ({ children }) => {
  const [theme, setThemeState] = useState(() => {
    const stored = getStoredTheme();
    return stored || "auto";
  });

  useEffect(() => {
    applyTheme(theme);
    saveTheme(theme);
  }, [theme]);

  useEffect(() => {
    const mql = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = () => {
      setThemeState((prev) => {
        if (prev === "auto") {
          applyTheme("auto");
        }
        return prev;
      });
    };
    mql.addEventListener("change", handler);
    return () => mql.removeEventListener("change", handler);
  }, []);

  const setTheme = useCallback((t) => {
    setThemeState(t);
  }, []);

  const toggleTheme = useCallback(() => {
    setThemeState((prev) => {
      const current = resolveTheme(prev);
      const next = current === "dark" ? "light" : "dark";
      return next;
    });
  }, []);

  const isDark = resolveTheme(theme) === "dark";

  return (
    <ThemeContext.Provider value={{ theme, isDark, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

ThemeProvider.propTypes = {
  children: PropTypes.node
};

export { ThemeContext, ThemeProvider };
