import React, { useState } from "react";
import { UpdateNotification } from "react-update-popup";
// import "react-update-popup/dist/index.css";

export const useVersionPopup = () => {
  const [latestVersion, setLatestVersion] = useState(null);
  const key_version = "last-frontend-version";

  // Function that checks if there is a new version
  const checkHasUpdate = async () => {
    try {
      const res = await fetch("/version.json", { cache: "no-store" });
      const data = await res.json();

      const storedVersion = localStorage.getItem(key_version);

      if (!storedVersion) {
        // First time load, store the version
        localStorage.setItem(key_version, data.tag);
        setLatestVersion(data.tag);
        return false; // no popup on first load
      }

      if (storedVersion !== data.tag) {
        setLatestVersion(data.tag);
        return true; // new version: popup shows
      }

      return false; // same version
    } catch (err) {
      console.error("Error checking version:", err);
      return false; // fallback
    }
  };

  const onReload = () => {
    if (latestVersion) {
      localStorage.setItem(key_version, latestVersion);
    }
    window.location.reload(true);
  };

  const VersionPopup = () => (
    <UpdateNotification
      title="New Version Available"
      description="There is a new version of the frontend. Refresh the page to update."
      buttonText="Refresh"
      refreshInterval={30_000} // every 30 seconds
      checkHasUpdate={checkHasUpdate}
      onReload={onReload}
    />
  );

  return { VersionPopup };
};

export default useVersionPopup;
