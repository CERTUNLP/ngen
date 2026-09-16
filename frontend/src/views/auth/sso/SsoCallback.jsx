import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { LOGIN } from "../../../store/actions";
import { COMPONENT_URL } from "../../../config/constant";
import { sessionPayload } from "../../../api/services/auth";
import store from "../../../store";
import Loader from "../../../components/Loader/Loader";

const SsoCallback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // The api answers with the code in the fragment, which the browser keeps to
    // itself: it never reaches a server log nor the referer of the page
    const fragment = new URLSearchParams(window.location.hash.replace(/^#/, ""));
    const exchangeCode = fragment.get("code");
    const nextUrl = fragment.get("next") || "/home";

    if (!exchangeCode) {
      navigate("/login", { replace: true });
      return;
    }

    const apiServer = localStorage.getItem("API_SERVER") || "";

    fetch(apiServer + COMPONENT_URL.ssoExchange, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code: exchangeCode })
    })
      .then((res) => {
        if (!res.ok) throw new Error("Exchange failed");
        return res.json();
      })
      .then((data) => {
        const { dispatch } = store;

        dispatch({
          type: LOGIN,
          payload: {
            user: data.user_data,
            ...sessionPayload(data.access_token)
          }
        });

        navigate(nextUrl, { replace: true });
      })
      .catch((error) => {
        console.error("SSO exchange error:", error);
        navigate("/login", { replace: true });
      });
  }, [navigate]);

  return <Loader />;
};

export default SsoCallback;
