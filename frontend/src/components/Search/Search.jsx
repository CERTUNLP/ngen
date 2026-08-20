import React, { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";

const Search = ({ type, setWordToSearch, wordToSearch, setLoading, setCurrentPage }) => {
  const [search, setSearch] = useState("");
  const skipBlurApplyRef = useRef(false);
  const { t } = useTranslation();

  useEffect(() => {
    if (!wordToSearch) {
      setSearch("");
      return;
    }

    if (wordToSearch.startsWith("search=")) {
      const value = wordToSearch.replace(/^search=/, "").replace(/&$/, "");
      setSearch(value);
    }
  }, [wordToSearch]);

  const searcher = (e) => {
    setSearch(e.target.value);
  };

  const action = () => {
    setWordToSearch("search=" + search + "&");
    if (wordToSearch !== "search=" + search + "&") {
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

  const handleButtonPointerDown = () => {
    skipBlurApplyRef.current = true;
  };

  const handleInputBlur = () => {
    if (skipBlurApplyRef.current) {
      skipBlurApplyRef.current = false;
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
      <button type="submit" className="search-btn btn btn-primary" onPointerDown={handleButtonPointerDown}>
        <i className="feather icon-search " />
      </button>
    </form>
  );
};

export default Search;
