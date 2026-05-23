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
    const accessToken = searchParams.get("access");
    const userParam = searchParams.get("user");
    const nextUrl = searchParams.get("next") || "/home";

    if (accessToken && userParam) {
      try {
        const user = JSON.parse(decodeURIComponent(userParam));
        const decoded = jwtDecode(accessToken);
        const { dispatch } = store;

        dispatch({
          type: LOGIN,
          payload: {
            user: user,
            token: accessToken,
            iat: decoded.iat,
            exp: decoded.exp,
            user_id: decoded.user_id
          }
        });

        navigate(nextUrl, { replace: true });
      } catch (error) {
        console.error("SSO callback error:", error);
        navigate("/login", { replace: true });
      }
    } else {
      navigate("/login", { replace: true });
    }
  }, [searchParams, navigate]);

  return <Loader />;
};

export default SsoCallback;
