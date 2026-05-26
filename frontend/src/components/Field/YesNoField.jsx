import React from "react";
import { Badge } from "react-bootstrap";
import { useTranslation } from "react-i18next";

const YesNoField = ({ value }) => {
  const { t } = useTranslation();
  return (
    <Badge bg={value ? "success" : "secondary"} pill style={{ fontSize: "0.8rem" }}>
      {value ? t("w.yes") : t("w.no")}
    </Badge>
  );
};

export default YesNoField;
