import React from "react";
import { Navigate } from "react-router-dom";
import { useSelector } from "react-redux";
import { BASE_URL, COMPONENT_URL } from "../../config/constant";

const GuestGuard = ({ children }) => {
  const account = useSelector((state) => state.account);
  const { isLoggedIn, last_url } = account;

  if (isLoggedIn) {
    const last_url_parsed = last_url ? last_url.replace("/", "") : "";
    const base_url = COMPONENT_URL.loginFrontend.replace("/", "");
    return <Navigate to={last_url_parsed && last_url_parsed !== base_url ? last_url : BASE_URL} />;
  }

  return <React.Fragment>{children}</React.Fragment>;
};

export default GuestGuard;
