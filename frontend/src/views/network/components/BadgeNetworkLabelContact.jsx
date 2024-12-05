import React, { useEffect, useState } from "react";
import { Badge } from "react-bootstrap";
import { getContact } from "../../../api/services/contacts";
import { useTranslation } from "react-i18next";

const BadgeNetworkLabelContact = (props) => {
  const [contact, setContact] = useState("");
  const { t } = useTranslation();

  useEffect(() => {
    showContactData(props.url);
  }, []);

  const showContactData = (url) => {
    getContact(url, true)
      .then((response) => {
        setContact(response.data);
      })
      .catch();
  };

  const labelRole = {
    technical: `${t("ngen.role.technical")}`,
    administrative: `${t("ngen.role.administrative")}`,
    abuse: `${t("ngen.role.abuse")}`,
    notifications: `${t("ngen.role.notifications")}`,
    noc: `${t("ngen.role.noc")}`
  };

  return (
    contact && (
      <React.Fragment>
        <Badge pill variant="info" className="mr-1">
          {contact.name + " (" + labelRole[`${contact.role}`] + ")"}
        </Badge>
        <br />
      </React.Fragment>
    )
  );
};

export default BadgeNetworkLabelContact;
