import React, { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import { LOGIN } from "../../../store/actions";
import store from "../../../store";
import Loader from "../../../components/Loader/Loader";

const SsoCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const exchangeCode = searchParams.get("code");
    const nextUrl = searchParams.get("next") || "/home";

    if (!exchangeCode) {
      navigate("/login", { replace: true });
      return;
    }

    const apiServer = localStorage.getItem("API_SERVER") || "";

    fetch(apiServer + "sso/exchange/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: exchangeCode })
    })
      .then((res) => {
        if (!res.ok) throw new Error("Exchange failed");
        return res.json();
      })
      .then((data) => {
        const decoded = jwtDecode(data.access_token);
        const { dispatch } = store;

        dispatch({
          type: LOGIN,
          payload: {
            user: data.user_data,
            token: data.access_token,
            iat: decoded.iat,
            exp: decoded.exp,
            user_id: decoded.user_id
          }
        });

        navigate(nextUrl, { replace: true });
      })
      .catch((error) => {
        console.error("SSO exchange error:", error);
        navigate("/login", { replace: true });
      });
  }, [searchParams, navigate]);

  return <Loader />;
};

export default SsoCallback;
