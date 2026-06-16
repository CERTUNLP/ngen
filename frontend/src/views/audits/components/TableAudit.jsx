import React, { useState } from "react";
import { Badge, Row, Spinner, Table } from "react-bootstrap";
import Ordering from "components/Ordering/Ordering";
import { useTranslation } from "react-i18next";

const ACTION_BADGE = { 0: "success", 1: "primary", 2: "danger" };
const ACTION_LABEL = { 0: "crud.add", 1: "crud.edit", 2: "crud.delete" };

const TableAudit = ({ audits, loading, order, setOrder, setLoading }) => {
  const { t } = useTranslation();
  const letterSize = {};
  const [expanded, setExpanded] = useState({});

  if (loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
      </Row>
    );
  }

  return (
    <Table responsive hover className="text-center">
      <thead>
        <tr>
          <Ordering field="timestamp" label={t("date.creation")} order={order} setOrder={setOrder} setLoading={setLoading} letterSize={letterSize} />
          <th>{t("reporter")}</th>
          <Ordering field="action" label={t("w.action")} order={order} setOrder={setOrder} setLoading={setLoading} letterSize={letterSize} />
          <th>{t("ngen.type")}</th>
          <th>{t("ngen.name_one")}</th>
          <th>{t("w.changes")}</th>
        </tr>
      </thead>
      <tbody>
        {audits.length === 0 ? (
          <tr>
            <td colSpan={6} className="text-muted py-4">{t("w.no_data")}</td>
          </tr>
        ) : (
          audits.map((a) => {
            const rowKey = a.id || a.url;
            const isExpanded = expanded[rowKey];
            return (
              <tr
                key={rowKey}
                onClick={() => setExpanded((prev) => ({ ...prev, [rowKey]: !isExpanded }))}
                style={{ cursor: "pointer" }}
              >
                <td className="text-nowrap">{a.timestamp?.slice(0, 16).replace("T", " ")}</td>
                <td>{a.actor?.username || "-"}</td>
                <td>
                  <Badge bg={ACTION_BADGE[a.action] || "secondary"}>
                    {t(ACTION_LABEL[a.action] || "w.unknown")}
                  </Badge>
                </td>
                <td className="text-nowrap">{a.content_type?.model || "-"}</td>
                <td className="text-start text-truncate" style={{ maxWidth: 200 }}>{a.object_repr || "-"}</td>
                <td className="text-start" style={{ maxWidth: isExpanded ? "none" : 250, overflow: isExpanded ? "visible" : "hidden", textOverflow: isExpanded ? "clip" : "ellipsis", whiteSpace: isExpanded ? "normal" : "nowrap" }}>
                  {a.changes
                    ? (() => {
                        try {
                          const parsed = typeof a.changes === "string" ? JSON.parse(a.changes) : a.changes;
                          if (parsed && typeof parsed === "object") {
                            return Object.entries(parsed).map(([k, v]) => (
                              <div key={k}><strong>{k}</strong>: {String(v[0])} → {String(v[1])}</div>
                            ));
                          }
                          return String(a.changes);
                        } catch {
                          return String(a.changes);
                        }
                      })()
                    : "-"}
                </td>
              </tr>
            );
          })
        )}
      </tbody>
    </Table>
  );
};

export default TableAudit;
