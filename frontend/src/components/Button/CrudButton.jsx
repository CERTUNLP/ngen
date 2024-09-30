import React from "react";
import { Button } from "react-bootstrap";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import PermissionCheck from "components/Auth/PermissionCheck";
import { routePermissions } from "utils/permissions";

const CrudButton = ({ type, name, onClick, disabled = false, to, state, permissions, checkPermRoute, text="", optionalPermissions}) => {
  const { t } = useTranslation();

  if (checkPermRoute) {
    // Find the permissions for the route
    permissions = routePermissions(to);
    // If the route not exist, component will not be rendered
    if (permissions === false) {
      return null;
    }
  }

  const button = {
    create: {
      class:  text ? "text-capitalize" : "text-capitalize",
      variant: "outline-primary",
      title: t("crud.add") + " " + name,
      icon: "fa fa-plus",
      text: text ? text : t("crud.add") + " " + name
    },
    read: {
      class:  text ? "text-capitalize" : "btn-icon btn-rounded",
      variant: "outline-primary",
      title: t("crud.detail"),
      icon: "fa fa-eye mx-auto",
      text:  text ? text : ""
    },
    edit: {
      class:  text ? "text-capitalize" : "btn-icon btn-rounded",
      variant: "outline-warning",
      title: t("crud.edit"),
      icon: "fa fa-edit",
      text:  text ? text : ""
    },
    delete: {
      class:  text ? "text-capitalize" : "btn-icon btn-rounded",
      variant: "outline-danger",
      title: t("crud.delete"),
      icon: "fas fa-trash-alt",
      text:  text ? text : ""
    },
    download: {
      class:  text ? "text-capitalize" : "text-capitalize",
      variant: "outline-danger",
      title: t("crud.download") + " " + name,
      icon: "fa fa-download",
      text:  text ? text : t("crud.download") + " " + name
    },
    plus: {
      class:  text ? "text-capitalize" : "btn-icon btn-rounded",
      variant: "outline-primary",
      title: t("crud.add"),
      icon: "fa fa-plus",
      text:  text ? text : ""
    },
    save: {
      class:  text ? "text-capitalize" : "btn-icon btn-rounded",
      variant: "outline-primary",
      title: t("crud.save"),
      icon: "fa fa-save",
      text:  text ? text : ""
    }
  };
  
  let component = (
    <Button
      className={button[type].class + " " + (disabled ? "btn-secondary disabled" : "")}
      variant={!disabled ? button[type].variant : ""}
      title={button[type].title}
      disabled={disabled}
      onClick={onClick}
    >
      <i className={button[type].icon} />
      {" " + button[type].text}
    </Button>
  );

  if (to && !disabled) {
    component = (
      <Link to={to} state={state}>
        {component}
      </Link>
    );
  }

  return (
    <PermissionCheck permissions={permissions} optionalPermissions={optionalPermissions}>
      {component}
    </PermissionCheck>
  );
};

export default CrudButton;
