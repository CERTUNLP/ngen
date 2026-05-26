import React, { useCallback, useEffect, useMemo, useState } from "react";
import { Button, Card, Col, Form, InputGroup, ListGroup, Row, Spinner, Table } from "react-bootstrap";
import { getAllSetting, patchSetting, uploadTeamLogo } from "../../api/services/setting";
import { useTranslation } from "react-i18next";
import UploadButton from "components/Button/UploadButton";
import PermissionCheck from "components/Auth/PermissionCheck";

const ACCENT = "#04a9f5";
const ACTIVE_BG = "#e8e9ed";

const sidebarStyle = {
  position: "sticky",
  top: 70,
  maxHeight: "calc(100vh - 100px)",
  overflowY: "auto"
};

const groupTitleStyle = {
  fontSize: "0.95rem",
  fontWeight: 600,
  letterSpacing: "0.5px",
  paddingLeft: 10,
  borderLeft: `3px solid ${ACCENT}`,
  marginBottom: 12,
  marginTop: 28
};

const EditSetting = () => {
  const [groups, setGroups] = useState({});
  const [groupOrder, setGroupOrder] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");
  const [activeGroup, setActiveGroup] = useState("");
  const [dirtyFields, setDirtyFields] = useState({});
  const [originals, setOriginals] = useState({});

  const { t } = useTranslation();

  useEffect(() => {
    getAllSetting()
      .then((data) => {
        const grouped = {};
        const order = [];
        data.forEach((item) => {
          const group = item.group || "";
          if (!grouped[group]) {
            grouped[group] = [];
            order.push(group);
          }
          grouped[group].push(item);
        });
        setGroups(grouped);
        setGroupOrder(order);
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  const filteredGroups = useMemo(() => {
    if (!filter.trim()) return { groups, order: groupOrder };
    const q = filter.toLowerCase();
    const fg = {};
    const fo = [];
    for (const gname of groupOrder) {
      const items = groups[gname];
      if (!items) continue;
      const matched = items.filter(
        (item) =>
          item.key.toLowerCase().includes(q) ||
          (item.help_text || "").toLowerCase().includes(q)
      );
      if (matched.length > 0) {
        fg[gname] = matched;
        fo.push(gname);
      }
    }
    return { groups: fg, order: fo };
  }, [filter, groups, groupOrder]);

  const handleScroll = useCallback(() => {
    const sections = document.querySelectorAll("[data-group]");
    let current = "";
    for (const section of sections) {
      const rect = section.getBoundingClientRect();
      if (rect.top <= 150) {
        current = section.getAttribute("data-group") || "";
      }
    }
    if (current) setActiveGroup(current);
  }, []);

  useEffect(() => {
    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener("scroll", handleScroll);
  }, [handleScroll, loading]);

  const scrollToGroup = (groupName) => {
    const el = document.getElementById("group-" + groupName.replace(/\s+/g, "-"));
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const PatchSetting = (url) => {
    let item = null;
    for (const g of Object.values(groups)) {
      const found = g.find((i) => i.url === url);
      if (found) { item = found; break; }
    }
    if (!item) return;

    patchSetting(url, item.key, item.value)
      .then(() => {
        setDirtyFields((prev) => {
          const next = { ...prev };
          delete next[url];
          return next;
        });
        setOriginals((prev) => {
          const next = { ...prev };
          delete next[url];
          return next;
        });
      })
      .catch((error) => console.log(error));
  };

  const rollbackField = (url) => {
    setGroups((prev) => {
      const updated = { ...prev };
      for (const gname of Object.keys(updated)) {
        const idx = updated[gname].findIndex((i) => i.url === url);
        if (idx !== -1) {
          updated[gname] = updated[gname].map((item, i) =>
            i === idx ? { ...item, value: originals[url] } : item
          );
          break;
        }
      }
      return updated;
    });
    setDirtyFields((prev) => {
      const next = { ...prev };
      delete next[url];
      return next;
    });
    setOriginals((prev) => {
      const next = { ...prev };
      delete next[url];
      return next;
    });
  };

  const uploadHandler = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    uploadTeamLogo(file);
  };

  const completeField = (event, groupName, url) => {
    const newValue = event.target.value;
    setGroups((prev) => {
      const updated = { ...prev };
      updated[groupName] = updated[groupName].map((item) => {
        if (item.url === url) {
          return { ...item, value: newValue };
        }
        return item;
      });
      return updated;
    });
    setDirtyFields((prev) => ({ ...prev, [url]: true }));
    setOriginals((prev) => {
      if (!(url in prev)) {
        let item = null;
        for (const g of Object.values(groups)) {
          const found = g.find((i) => i.url === url);
          if (found) { item = found; break; }
        }
        return { ...prev, [url]: item?.value };
      }
      return prev;
    });
  };

  const renderTable = (items) => (
    <Table responsive hover className="text-center mb-4" size="sm">
      <thead className="table-light">
        <tr>
          <th style={{ width: "18%" }}>{t("ngen.name_one")}</th>
          <th style={{ width: "49%" }}>{t("ngen.description")}</th>
          <th style={{ width: "23%" }}>{t("ngen.value")}</th>
          <PermissionCheck permissions="change_constance">
            <th style={{ width: "10%" }}>{t("w.modify")}</th>
          </PermissionCheck>
        </tr>
      </thead>
      <tbody>
        {items.map((setting, index) => {
          const isDirty = setting.url in dirtyFields;
          return (
            <tr key={index}>
              <td className="fw-bold align-middle" style={{ whiteSpace: "nowrap" }}>{setting.key}</td>
              <td className="align-middle">
                <Form.Control
                  as="textarea"
                  rows={2}
                  readOnly
                  value={setting.help_text || ""}
                  className="text-body"
                  style={{ resize: "none", backgroundColor: "transparent", border: "none", boxShadow: "none", fontSize: "0.85rem", padding: 0, wordBreak: "break-word" }}
                />
                <small
                  className="text-muted fst-italic text-start"
                  style={{
                    display: "block",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                    paddingLeft: 0
                  }}
                  title={setting.default?.toString() || ""}
                >
                  {t("settings.default.label")} {setting.default?.toString() || ""}
                </small>
              </td>
              <td className="align-middle">
                {setting.editable && setting.key !== "TEAM_LOGO" ? (
                  <Form.Group controlId={`formGrid-${setting.key}`}>
                    <Form.Control
                      name="value"
                      value={setting.value?.toString() || ""}
                      maxLength="500"
                      placeholder={t("w.issue.placeholder")}
                      onChange={(e) => completeField(e, setting.group, setting.url)}
                    />
                  </Form.Group>
                ) : (
                  <span className="text-muted">{setting.value?.toString()}</span>
                )}
              </td>
              <PermissionCheck permissions="change_constance">
              <td className="align-middle">
                  {setting.editable && setting.key !== "TEAM_LOGO" ? (
                    <div className="d-flex justify-content-center gap-1">
                      <Button
                        size="sm"
                        variant={isDirty ? "outline-success" : "outline-secondary"}
                        disabled={!isDirty}
                        onClick={() => PatchSetting(setting.url)}
                        title={t("button.save")}
                      >
                        <i className="feather icon-check" />
                      </Button>
                      <Button
                        size="sm"
                        variant={isDirty ? "outline-warning" : "outline-secondary"}
                        disabled={!isDirty}
                        onClick={() => rollbackField(setting.url)}
                        title={t("settings.undo")}
                      >
                        <i className="feather icon-rotate-ccw" />
                      </Button>
                    </div>
                  ) : setting.key === "TEAM_LOGO" ? (
                    <UploadButton variant="outline-warning" text={t("w.upload")} uploadHandler={uploadHandler} />
                  ) : (
                    <></>
                  )}
                </td>
              </PermissionCheck>
            </tr>
          );
        })}
      </tbody>
    </Table>
  );

  const renderStaticTable = (items) => (
    <Table responsive hover className="text-center mb-4" size="sm">
      <thead className="table-light">
        <tr>
          <th style={{ width: "25%" }}>{t("ngen.name_one")}</th>
          <th style={{ width: "35%" }}>{t("ngen.default")}</th>
          <th style={{ width: "40%" }}>{t("ngen.value")}</th>
        </tr>
      </thead>
      <tbody>
        {items.map((setting, index) => (
          <tr key={index}>
            <td className="fw-bold align-middle" style={{ whiteSpace: "nowrap" }}>{setting.key}</td>
            <td className="text-muted small align-middle">{setting.default?.toString()}</td>
            <td className="text-muted align-middle">{setting.value?.toString()}</td>
          </tr>
        ))}
      </tbody>
    </Table>
  );

  return (
    <div>
      <Card>
        <Card.Header>
          <Card.Title as="h5">{t("systemConfig")}</Card.Title>
        </Card.Header>
        <Card.Body>
          {loading ? (
            <Row className="justify-content-md-center my-5">
              <Spinner animation="border" variant="primary" />
            </Row>
          ) : (
            <Row>
              <Col md={2}>
                <div style={sidebarStyle}>
                  <div style={{ marginBottom: 12 }}>
                    <InputGroup size="sm">
                      <InputGroup.Text>
                        <i className="feather icon-search" style={{ fontSize: "0.8rem" }} />
                      </InputGroup.Text>
                      <Form.Control
                        type="text"
                        placeholder={t("settings.filter.placeholder")}
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        className="shadow-none"
                        style={{ boxShadow: "none" }}
                      />
                      {filter && (
                        <Button variant="outline-secondary" size="sm" onClick={() => setFilter("")}>
                          <i className="feather icon-x" />
                        </Button>
                      )}
                    </InputGroup>
                  </div>
                  <ListGroup variant="flush">
                    {filteredGroups.order.map((groupName) => {
                      const name = groupName || "Other";
                      const active = activeGroup === groupName;
                      return (
                        <ListGroup.Item
                          key={groupName}
                          action
                          className="py-2 px-3 border-0"
                          style={{
                            fontSize: "0.88rem",
                            backgroundColor: active ? ACTIVE_BG : undefined,
                            fontWeight: active ? 500 : undefined
                          }}
                          onClick={() => scrollToGroup(groupName)}
                        >
                          {name}
                        </ListGroup.Item>
                      );
                    })}
                  </ListGroup>
                </div>
              </Col>
              <Col md={10}>
                {filteredGroups.order.length === 0 ? (
                  <p className="text-muted text-center my-5">
                    {filter.trim() ? t("settings.filter.no_results") : t("settings.filter.empty")}
                  </p>
                ) : (
                  filteredGroups.order.map((groupName) => (
                    <div
                      key={groupName}
                      id={"group-" + groupName.replace(/\s+/g, "-")}
                      data-group={groupName}
                      className="mb-2"
                    >
                      <h6 style={groupTitleStyle}>
                        {groupName || "Other"}
                      </h6>
                      {groupName === "Environment / Static"
                        ? renderStaticTable(filteredGroups.groups[groupName])
                        : renderTable(filteredGroups.groups[groupName])}
                    </div>
                  ))
                )}
              </Col>
            </Row>
          )}
        </Card.Body>
      </Card>
    </div>
  );
};

export default EditSetting;
