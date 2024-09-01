import React from "react";
import { Navigate } from "react-router-dom";
import { useSelector } from "react-redux";
import { BASE_URL, COMPONENT_URL } from "../../config/constant";

const GuestGuard = ({ children }) => {
  const account = useSelector((state) => state.account);
  const { isLoggedIn, last_url } = account;

  if (isLoggedIn) {
    return <Navigate to={last_url && last_url !== COMPONENT_URL.loginFrontend ? last_url : BASE_URL} />;
  }

  return <React.Fragment>{children}</React.Fragment>;
};

export default GuestGuard;
