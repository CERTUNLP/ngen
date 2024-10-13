import React, { useEffect, useState } from "react";
import { Button } from "react-bootstrap";
import { useTranslation } from "react-i18next";

const YesNoField = ({ value }) => {
  const { t } = useTranslation();
  
  const [stateBool, setStateBool] = useState(null);

  useEffect(() => {
    setStateBool(value);
  }, [value]);
    
  return (
    <React.Fragment>
      <p>{stateBool ? t("w.yes") : t("w.no")}</p>
    </React.Fragment>
  );
};

export default YesNoField;
