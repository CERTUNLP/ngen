import React from "react";
import { Badge } from "react-bootstrap";
import { useQuery } from "@tanstack/react-query";
import { getQueryUser } from "api/services/users";

const BadgeUserLabel = ({ url }) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ["userKey"],
    queryFn: getQueryUser,
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  });

  if (!url || isLoading || error) return null;

  const user = data?.[url];
  if (!user?.username) return null;

  return (
    <Badge pill bg="info" className="mr-1">
      {user.username}
    </Badge>
  );
};

export default BadgeUserLabel;

  if (!username) return null;

  return (
    <Badge pill bg="info" className="mr-1">
      {username}
    </Badge>
  );
};

export default BadgeUserLabel;
