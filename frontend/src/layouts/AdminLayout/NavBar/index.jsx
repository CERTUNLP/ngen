import React, { useContext } from "react";
import { Link } from "react-router-dom";

import { ConfigContext } from "../../../contexts/ConfigContext";
import NavRight from "./NavRight";
import * as actionType from "../../../store/actions";

const NavBar = ({ children }) => {
  const configContext = useContext(ConfigContext);
  const { collapseMenu, headerFixedLayout, layout } = configContext.state;
  const { dispatch } = configContext;

  let headerClass = ["navbar", "pcoded-header", "navbar-expand-lg"];
  if (headerFixedLayout && layout === "vertical") {
    headerClass = [...headerClass, "headerpos-fixed"];
  }

  let toggleClass = ["mobile-menu"];
  if (collapseMenu) {
    toggleClass = [...toggleClass, "on"];
  }

  const navToggleHandler = () => {
    dispatch({ type: actionType.COLLAPSE_MENU });
  };

  let navBar = (
    <React.Fragment>
      <div className="m-header">
        <Link to="#" className={toggleClass.join(" ")} id="mobile-collapse" onClick={navToggleHandler}>
          <span />
        </Link>
        <Link to="#" className="b-brand">
          <img src={localStorage.getItem("API_SERVER") + "static/img/ngenlogo_inv_light.png"} alt="NGEN" className="logo" id="teamlogo" />
        </Link>
      </div>
      <div className="header-toolbar">
        <div className="header-breadcrumb">{children}</div>
        <NavRight />
      </div>
    </React.Fragment>
  );

  return (
    <React.Fragment>
      <header className={headerClass.join(" ")}>{navBar}</header>
    </React.Fragment>
  );
};

export default NavBar;
