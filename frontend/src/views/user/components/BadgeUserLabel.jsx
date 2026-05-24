import React, { useEffect, useState } from "react";
import { Badge } from "react-bootstrap";
import apiInstance from "../../../api/api";

const BadgeUserLabel = ({ url }) => {
  const [username, setUsername] = useState("");

  useEffect(() => {
    apiInstance
      .get(url)
      .then((response) => {
        setUsername(response.data.username);
      })
      .catch(() => {});
  }, [url]);

  if (!username) return null;

  return (
    <Badge pill bg="info" className="mr-1">
      {username}
    </Badge>
  );
};

export default BadgeUserLabel;
