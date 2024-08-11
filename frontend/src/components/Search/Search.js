import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';

const Search = ({ type, setWordToSearch, wordToSearch, setLoading }) => {
  const [search, setSearch] = useState("");
  const { t } = useTranslation();

  const searcher = (e) => {
    setSearch(e.target.value);
  };

  const action = () => {
    console.log("search=" + search + '&');
    setWordToSearch("search=" + search + '&');
    if (wordToSearch !== "search=" + search + '&') {
      setLoading(true);
    }
  };

  const text = `${t('search')} ${type} `;

  const handleSubmit = (e) => {
    e.preventDefault(); // Evita que se envíe el formulario (recarga la página)
    action();
  };

  return (
    <form onSubmit={handleSubmit} className="input-group">
      <input value={search} onChange={searcher} type="text" id="m-search" className="form-control" placeholder={text}/>
      <button type="submit" className="search-btn btn btn-primary">
        <i className="feather icon-search "/>
      </button>
    </form>
  );
};

export default Search;
