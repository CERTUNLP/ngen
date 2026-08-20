import { useEffect, useState } from "react";
import { getHealthStatus, subscribeHealth, releaseLeadership } from "api/services/health";

const useBackendHealth = () => {
  const [status, setStatus] = useState(() => getHealthStatus());

  useEffect(() => {
    const unsubscribe = subscribeHealth(setStatus);

    const onVisibilityChange = () => {
      if (!document.hidden) {
        setStatus(getHealthStatus());
      }
    };
    document.addEventListener("visibilitychange", onVisibilityChange);

    return () => {
      unsubscribe();
      releaseLeadership();
      document.removeEventListener("visibilitychange", onVisibilityChange);
    };
  }, []);

  return status === "up";
};

export default useBackendHealth;
