import React from "react";
import { BrowserRouter } from "react-router-dom";

import routes, { renderRoutes } from "routes";
import Alert from "components/Alert/Alert";
import { useTokenManager } from "hooks/useTokenManager";
import { useVersionPopup } from "hooks/useVersionPopup";

const App = () => {
  useTokenManager();

  const { VersionPopup } = useVersionPopup();

  return (
    <>
      <Alert component="all" />
      <BrowserRouter basename={import.meta.env.VITE_APP_BASE_NAME}>
        {renderRoutes(routes)}
      </BrowserRouter>
      <VersionPopup />
    </>
  );
};

export default App;
