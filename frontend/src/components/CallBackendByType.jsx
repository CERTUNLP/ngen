import React, { useEffect, useState } from "react";
import LetterFormat from "./LetterFormat";

const CallBackendByType = ({ url, callback, useBadge }) => {
  const [data, setData] = useState("");

  useEffect(() => {
    callback(url, setData);
  }, []);

  return (
    data && (
      <React.Fragment>
        <LetterFormat useBadge={useBadge} stringToDisplay={data.value} color={data.color} />
      </React.Fragment>
    )
  );
};

export default CallBackendByType;
