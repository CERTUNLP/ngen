import React, { useState, useEffect } from "react";
import { Badge, OverlayTrigger, Popover, Spinner } from "react-bootstrap";
import { getAddressInfo } from "api/services/tools";
import { useTranslation } from "react-i18next";

const CidrContactTooltip = ({ address_value }) => {
  const { t } = useTranslation();
  const [contacts, setContacts] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fetched, setFetched] = useState(false);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    setContacts(null);
    setLoading(false);
    setFetched(false);
    setHasError(false);
  }, [address_value]);

  const fetchContacts = () => {
    if ((fetched && !hasError) || loading) return;
    setLoading(true);
    setHasError(false);
    getAddressInfo(address_value, { with_contacts: true })
      .then((data) => {
        setContacts(data?.data?.contacts || []);
        setFetched(true);
      })
      .catch(() => {
        setHasError(true);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const labelRole = {
    technical: t("ngen.role.technical"),
    administrative: t("ngen.role.administrative"),
    abuse: t("ngen.role.abuse"),
    notifications: t("ngen.role.notifications"),
    noc: t("ngen.role.noc"),
  };

  const popover = (
    <Popover id={`popover-cidr-contacts-${address_value}`} style={{ maxWidth: "320px" }}>
      <Popover.Header as="h3">{t("ngen.contact_other")}</Popover.Header>
      <Popover.Body>
        {loading ? (
          <div className="text-center">
            <Spinner animation="border" size="sm" />
          </div>
        ) : hasError ? (
          <span className="text-danger" style={{ fontSize: "0.85em" }}>
            {t("ngen.contactcheck.error")}
          </span>
        ) : contacts && contacts.length > 0 ? (
          contacts.map((c, idx) => (
            <div key={idx} className="mb-1">
              <Badge pill bg="info" className="me-1">
                {labelRole[c.role] || c.role}
              </Badge>
              <strong>{c.name}</strong>
              {c.username && (
                <div>
                  <small className="text-muted">{c.username}</small>
                </div>
              )}
            </div>
          ))
        ) : (
          <span className="text-muted">-</span>
        )}
      </Popover.Body>
    </Popover>
  );

  return (
    <OverlayTrigger
      trigger={["hover", "focus"]}
      placement="right"
      overlay={popover}
      onToggle={(show) => { if (show) fetchContacts(); }}
    >
      <span
        tabIndex={0}
        role="button"
        aria-label={`${t("ngen.contact_other")}: ${address_value}`}
        style={{ cursor: "default", textDecoration: "underline dotted" }}
      >
        {address_value}
      </span>
    </OverlayTrigger>
  );
};

export default CidrContactTooltip;
