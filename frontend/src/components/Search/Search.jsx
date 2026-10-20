import React, { useEffect, useRef, useState } from "react";
import { OverlayTrigger, Tooltip } from "react-bootstrap";
import { useTranslation } from "react-i18next";

const EXACT_MODE_PARAM = "search_mode=exact&";

const buildSearchQuery = (text, exact) => (text ? "search=" + encodeURIComponent(text) + "&" + (exact ? EXACT_MODE_PARAM : "") : "");

const parseSearchQuery = (query) => {
  const match = /^search=([^&]*)&/.exec(query || "");
  return { text: match ? decodeURIComponent(match[1]) : "", exact: (query || "").includes(EXACT_MODE_PARAM) };
};

const Search = ({ type, setWordToSearch, wordToSearch, setLoading, setCurrentPage }) => {
  const [search, setSearch] = useState("");
  const [exact, setExact] = useState(false);
  const skipBlurApplyRef = useRef(false);
  const { t } = useTranslation();

  useEffect(() => {
    if (!wordToSearch) {
      setSearch("");
      return;
    }

    if (wordToSearch.startsWith("search=")) {
      const parsed = parseSearchQuery(wordToSearch);
      setSearch(parsed.text);
      setExact(parsed.exact);
    }
  }, [wordToSearch]);

  const searcher = (e) => {
    setSearch(e.target.value);
  };

  const action = (exactMode = exact) => {
    const query = buildSearchQuery(search, exactMode);
    setWordToSearch(query);
    if (wordToSearch !== query) {
      if (setCurrentPage) {
        setCurrentPage(1);
      }
      setLoading(true);
    }
  };

  const text = `${t("search")} ${type} `;

  const handleSubmit = (e) => {
    e.preventDefault(); // Evita que se envíe el formulario (recarga la página)
    action();
    skipBlurApplyRef.current = false;
  };

  const clearSearch = () => {
    skipBlurApplyRef.current = false;
    setSearch("");
    if (wordToSearch) {
      setWordToSearch("");
      if (setCurrentPage) {
        setCurrentPage(1);
      }
      setLoading(true);
    }
  };

  const toggleExact = () => {
    skipBlurApplyRef.current = false;
    const nextExact = !exact;
    setExact(nextExact);
    if (search) {
      action(nextExact);
    }
  };

  const handleButtonPointerDown = () => {
    skipBlurApplyRef.current = true;
  };

  const handleInputBlur = () => {
    if (skipBlurApplyRef.current) {
      skipBlurApplyRef.current = false;
      return;
    }
    if (buildSearchQuery(search, exact) === (wordToSearch || "")) {
      return;
    }
    action();
  };

  return (
    <form onSubmit={handleSubmit} className="search-input-group">
      <div className="search-field">
        <input
          value={search}
          onChange={searcher}
          onBlur={handleInputBlur}
          type="text"
          id="m-search"
          className="form-control"
          placeholder={text}
        />
        {search && (
          <button
            type="button"
            className="search-clear-btn"
            onClick={clearSearch}
            onPointerDown={handleButtonPointerDown}
            aria-label={t("search.clear")}
          >
            <i className="feather icon-x" />
          </button>
        )}
      </div>
      <OverlayTrigger placement="top" overlay={<Tooltip id="search-exact-tooltip">{t("search.exact.tooltip")}</Tooltip>}>
        <button
          type="button"
          className={`search-exact-btn btn ${exact ? "btn-primary" : "btn-outline-secondary"}`}
          onClick={toggleExact}
          onPointerDown={handleButtonPointerDown}
          aria-pressed={exact}
          aria-label={t("search.exact")}
        >
          <i className="feather icon-crosshair" />
        </button>
      </OverlayTrigger>
      <button type="submit" className="search-btn btn btn-primary" onPointerDown={handleButtonPointerDown}>
        <i className="feather icon-search " />
      </button>
    </form>
  );
};

export default Search;
