import { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { COMPONENT_URL } from "config/constant";
import {
  publishHealthStatus,
  readCachedStatus,
  subscribeHealthStatus,
  subscribeLeadership,
  writeCachedStatus
} from "api/services/backendHealth";

const fetchHealth = async () => {
  const apiServer = localStorage.getItem("API_SERVER");
  if (!apiServer) {
    throw new Error("API_SERVER is not set");
  }
  const res = await fetch(apiServer + COMPONENT_URL.health, { cache: "no-store" });
  if (!res.ok) {
    throw new Error("Backend health check failed");
  }
  return res.json();
};

const useBackendHealth = () => {
  const queryClient = useQueryClient();
  const [isLeader, setIsLeader] = useState(false);

  useEffect(() => subscribeLeadership(setIsLeader), []);

  useEffect(
    () =>
      subscribeHealthStatus((status) => {
        writeCachedStatus(status);
        queryClient.setQueryData(["backend-health"], { status });
      }),
    [queryClient]
  );

  const query = useQuery({
    queryKey: ["backend-health"],
    queryFn: fetchHealth,
    refetchInterval: isLeader ? 3000 : false,
    refetchIntervalInBackground: true,
    retry: false,
    staleTime: Infinity,
    initialData: () => {
      const cached = readCachedStatus();
      return cached ? { status: cached } : undefined;
    }
  });

  useEffect(() => {
    if (!isLeader) return;
    const status = query.isError ? "down" : query.data?.status;
    if (status) {
      writeCachedStatus(status);
      publishHealthStatus(status);
    }
  }, [isLeader, query.data, query.isError]);

  return !query.isError && query.data?.status === "ok";
};

export default useBackendHealth;
