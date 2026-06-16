import React, { useEffect, useRef, useState } from "react";
import { Badge, Button, Modal, Row, Spinner, Table } from "react-bootstrap";
import { Link } from "react-router-dom";
import { getObjectAudits } from "api/services/audit";
import { useTranslation } from "react-i18next";
import PermissionCheck from "components/Auth/PermissionCheck";

const ACTION_BADGE = { 0: "success", 1: "primary", 2: "danger" };
const ACTION_LABEL = { 0: "crud.add", 1: "crud.edit", 2: "crud.delete" };

const AuditModal = ({ show, onHide, modelName, objectId }) => {
  const { t } = useTranslation();
  const [audits, setAudits] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  const [page, setPage] = useState(1);
  const [expanded, setExpanded] = useState({});
  const tableEndRef = useRef(null);

  useEffect(() => {
    if (show && modelName && objectId) {
      setPage(1);
      setAudits([]);
      loadAudits(1);
    }
  }, [show, modelName, objectId]);

  useEffect(() => {
    if (page > 1 && tableEndRef.current) {
      tableEndRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [audits.length]);

  const loadAudits = (pageNum) => {
    setLoading(true);
    getObjectAudits(modelName, objectId, pageNum)
      .then((response) => {
        setAudits((prev) => pageNum === 1 ? response.data.results : [...prev, ...response.data.results]);
        setHasMore(!!response.data.next);
        setPage(pageNum);
      })
      .finally(() => setLoading(false));
  };

  const renderChanges = (changes) => {
    if (!changes) return "-";
    try {
      const parsed = typeof changes === "string" ? JSON.parse(changes) : changes;
      if (!parsed || Object.keys(parsed).length === 0) return "-";
      return Object.entries(parsed).map(([field, values]) => (
        <div key={field} className="text-start">
          <strong>{field}:</strong>{" "}
          <span className="text-muted">{renderValue(values[0])}</span>
          {" → "}
          <span>{renderValue(values[1])}</span>
        </div>
      ));
    } catch {
      return String(changes);
    }
  };

  const renderValue = (value) => {
    if (!value) return String(value ?? "-");
    const str = String(value);
    const m2mMatch = str.match(/^(post_add|post_remove|post_clear)\s+\[(\w+)\]:\s*\[([^\]]+)\]$/);
    if (m2mMatch) {
      const [, action, model, pksStr] = m2mMatch;
      const pks = pksStr.split(",").map((s) => s.trim()).filter(Boolean);
      return (
        <>
          {action}{" "}
          {pks.map((pk, i) => (
            <React.Fragment key={pk}>
              {i > 0 && ", "}
              <Link to={`/${model}s/view/${pk}`}>{pk}</Link>
            </React.Fragment>
          ))}
        </>
      );
    }
    return str;
  };

  return (
    <PermissionCheck permissions={["view_logentry"]}>
      <Modal show={show} onHide={onHide} size="lg" centered>
        <Modal.Header closeButton>
          <Modal.Title>
            {t("ngen.audit.title")}: {modelName} #{objectId}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {loading ? (
            <p className="text-muted text-center py-4">{t("w.loading")}</p>
          ) : audits.length === 0 ? (
            <p className="text-muted text-center py-4">{t("w.no_data")}</p>
          ) : (
            <>
              <Table responsive hover size="sm">
                <thead>
                  <tr>
                    <th>{t("date.creation")}</th>
                    <th>{t("reporter")}</th>
                    <th>{t("w.action")}</th>
                    <th>{t("w.changes")}</th>
                  </tr>
                </thead>
                <tbody>
                  {audits.map((a) => {
                    const isExpanded = expanded[a.id || a.url];
                    return (
                      <tr
                        key={a.id || a.url}
                        onClick={() => setExpanded((prev) => ({ ...prev, [a.id || a.url]: !isExpanded }))}
                        style={{ cursor: "pointer" }}
                      >
                        <td className="text-nowrap">
                          {a.timestamp?.slice(0, 16).replace("T", " ")}
                        </td>
                        <td>{a.actor?.username || "-"}</td>
                        <td>
                          <Badge bg={ACTION_BADGE[a.action] || "secondary"}>
                            {t(ACTION_LABEL[a.action] || "w.unknown")}
                          </Badge>
                        </td>
                        <td style={{ maxWidth: isExpanded ? "none" : 300, whiteSpace: isExpanded ? "normal" : "nowrap", overflow: isExpanded ? "visible" : "hidden", textOverflow: isExpanded ? "clip" : "ellipsis" }}>
                          {renderChanges(a.changes)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </Table>
              {hasMore && (
                <Row className="justify-content-center py-2">
                  {loading ? (
                    <Spinner animation="border" variant="primary" size="sm" />
                  ) : (
                    <Button variant="outline-primary" size="sm" type="button" onClick={() => loadAudits(page + 1)}>
                      {t("w.load_more")}
                    </Button>
                  )}
                  <div ref={tableEndRef} />
                </Row>
              )}
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <button type="button" className="btn btn-outline-secondary" onClick={onHide}>
            {t("w.close")}
          </button>
        </Modal.Footer>
      </Modal>
    </PermissionCheck>
  );
};

export default AuditModal;
