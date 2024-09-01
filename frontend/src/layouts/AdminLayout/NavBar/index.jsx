import React, { useContext, useState } from "react";
import { Link } from "react-router-dom";
import { API_SERVER } from "../../../config/constant";

import { ConfigContext } from "../../../contexts/ConfigContext";
import * as actionType from "../../../store/actions";

const NavBar = () => {
  const [moreToggle, setMoreToggle] = useState(false);
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

  let moreClass = ["mob-toggler"];

  let collapseClass = ["collapse navbar-collapse"];
  if (moreToggle) {
    moreClass = [...moreClass, "on"];
    collapseClass = [...collapseClass, "show"];
  }

  let navBar = (
    <React.Fragment>
      <div className="m-header">
        <Link to="#" className={toggleClass.join(" ")} id="mobile-collapse" onClick={navToggleHandler}>
          <span />
        </Link>
        <Link to="#" className="b-brand">
          <img src={API_SERVER + "static/img/ngenlogo_inv_light.png"} alt="NGEN" className="logo" id="teamlogo" />
        </Link>
        {/*<Link to="#" className={moreClass.join(' ')}*/}
        {/*      onClick={() => setMoreToggle(!moreToggle)}>*/}
        {/*  <i className="feather icon-more-vertical"/>*/}
        {/*</Link>*/}
      </div>
      {/*<div style={{ justifyContent: 'space-between' }}*/}
      {/*     className={collapseClass.join(' ')}>*/}
      {/*  <NavLeft/>*/}
      {/*  <NavRight/>*/}
      {/*</div>*/}
    </React.Fragment>
  );

  return (
    <React.Fragment>
      <header className={headerClass.join(" ")}>{navBar}</header>
    </React.Fragment>
  );
};

export default NavBar;
