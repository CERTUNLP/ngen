import React, { useEffect, useState } from "react";
import { Button } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { userIsSuperuser, currentUserHasPermissions, userIsStaff } from "utils/permissions";

const ActiveButton = ({ active, onClick, permissions, disabled=false }) => {
  const { t } = useTranslation();

  const [stateBool, setStateBool] = useState(null);

  useEffect(() => {
    setStateBool(active);
  }, [active]);

  const isEnabled = !disabled && currentUserHasPermissions(permissions);

  return (
    <React.Fragment>
      <Button
        className={"btn-icon btn-rounded" + (isEnabled ? "" : " disabled")}
        variant={stateBool ? "outline-success" : "outline-danger"}
        title={stateBool ? t("w.active") : t("w.inactive")}
        onClick={isEnabled ? onClick : null}
      >
        <i className={stateBool ? "feather icon-check" : "feather icon-x"}></i>
      </Button>
    </React.Fragment>
  );
};

export default ActiveButton;
