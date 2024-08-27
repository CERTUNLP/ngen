import React, { useEffect, useState } from "react";
import { Button } from "react-bootstrap";
import { useTranslation } from "react-i18next";

const ActiveButton = ({ active, onClick }) => {
  const { t } = useTranslation();

  const [stateBool, setStateBool] = useState(null);

  useEffect(() => {
    setStateBool(active);
  }, [active]);

  return (
    <React.Fragment>
      <Button
        className="btn-icon btn-rounded"
        variant={stateBool ? "outline-success" : "outline-danger"}
        title={stateBool ? t("w.active") : t("w.inactive")}
        onClick={onClick}
      >
        <i className={stateBool ? "feather icon-check-circle" : "feather icon-alert-triangle"} />
      </Button>
    </React.Fragment>
  );
};

export default ActiveButton;
