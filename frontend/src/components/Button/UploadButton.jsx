import React, { useRef } from "react";
import { Button } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import PermissionCheck from "components/Auth/PermissionCheck";

const UploadButton = ({ name, disabled = false, permissions, text = "", optionalPermissions, uploadHandler }) => {
  const { t } = useTranslation();
  const fileInputRef = useRef();

  const button = {
    class: text ? "text-capitalize" : "text-capitalize",
    variant: "outline-primary",
    title: t("w.upload") + " " + name,
    icon: "fa fa-upload",
    text: text ? text : t("w.upload") + " " + name
  };

  let component = (
    <>
      <Button
        className={button.class + " " + (disabled ? "btn-secondary disabled" : "")}
        variant={!disabled ? button.variant : ""}
        title={button.title}
        disabled={disabled}
        onClick={() => fileInputRef.current.click()}
      >
        <i className={button.icon} />
        {" " + button.text}
      </Button>
      <input onChange={uploadHandler} multiple={false} ref={fileInputRef} type="file" hidden />
    </>
  );

  return (
    <PermissionCheck permissions={permissions} optionalPermissions={optionalPermissions}>
      {component}
    </PermissionCheck>
  );
};

export default UploadButton;
