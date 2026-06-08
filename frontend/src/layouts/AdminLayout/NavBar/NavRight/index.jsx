import React, { useContext } from "react";
import { Dropdown } from "react-bootstrap";
import { Link } from "react-router-dom";
import { useSelector } from "react-redux";
import { useTranslation } from "react-i18next";
import i18n from "i18next";
import { ThemeContext } from "../../../../contexts/ThemeContext";

const CURRENT_LANG = (i18n.language || localStorage.getItem("NGEN_LANG") || "en").substring(0, 2);

const NavRight = () => {
  const { t } = useTranslation();
  const { isDark, toggleTheme } = useContext(ThemeContext);
  const user = useSelector((state) => state.account?.user);
  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const lang = i18n.language?.substring(0, 2) || CURRENT_LANG;

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
    localStorage.setItem("NGEN_LANG", lng);
  };

  const displayName = user?.username || user?.first_name || "";

  return (
    <ul className="navbar-nav ms-auto">
      <Dropdown as="li" className="nav-item" align="end">
        <Dropdown.Toggle as="button" className="nav-link user-dropdown-toggle btn btn-link">
          <i className="feather icon-user" />
          <span className="user-name">{displayName}</span>
        </Dropdown.Toggle>
        <Dropdown.Menu className="user-panel-menu">
          <div className="user-info-header">
            <div className="user-avatar">
              <i className="feather icon-user" />
            </div>
            <div>
              <strong>{user?.first_name ? `${user.first_name} ${user.last_name || ""}` : displayName}</strong>
              {user?.username && user?.first_name && <small className="d-block">@{user.username}</small>}
            </div>
          </div>

          <Dropdown.Divider />

          <Dropdown.Item as="button" className="pref-item" onClick={toggleTheme}>
            <i className={isDark ? "feather icon-sun" : "feather icon-moon"} />
            <span>{t("ngen.dark_mode")}</span>
            <span className="ms-auto">
              <i className={isDark ? "fas fa-toggle-on text-primary" : "fas fa-toggle-off text-muted"} />
            </span>
          </Dropdown.Item>

          {["en", "es"].map((lng) => (
            <Dropdown.Item
              key={lng}
              as="button"
              className={`pref-item${lang === lng ? " active-lang" : ""}`}
              onClick={() => changeLanguage(lng)}
            >
              <i className="feather icon-globe" />
              <span>{lng.toUpperCase()}</span>
              {lang === lng && <i className="fas fa-check ms-auto text-success" />}
            </Dropdown.Item>
          ))}

          <Dropdown.Item as="div" className="pref-item">
            <i className="feather icon-clock" />
            <span>{tz}</span>
          </Dropdown.Item>

          <Dropdown.Divider />

          <Dropdown.Item as={Link} to="/profile" className="pref-item">
            <i className="feather icon-user" />
            <span>{t("ngen.user.profile")}</span>
          </Dropdown.Item>

          <Dropdown.Item
            as={Link}
            to="/logout/"
            className="pref-item"
            onClick={() => {
              localStorage.removeItem("ngen-account");
            }}
          >
            <i className="feather icon-log-out" />
            <span>{t("button.logout")}</span>
          </Dropdown.Item>
        </Dropdown.Menu>
      </Dropdown>
    </ul>
  );
};

export default NavRight;
