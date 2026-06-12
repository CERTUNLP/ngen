import React, { useEffect, useState } from "react";
import { Button, Col, Form, Row, Spinner } from "react-bootstrap";
import { validateName } from "../../../utils/validators/feed";
import { getMinifiedPermissions } from "api/services/permissions";
import DualListBox from "react-dual-listbox";
import CrudButton from "components/Button/CrudButton";
import { useTranslation } from "react-i18next";

const FormGroup = ({ name, setName, permissions, setPermissions, createGroup, loading }) => {
  const [permissionOptions, setPermissionOptions] = useState([]);
  const { t } = useTranslation();

  useEffect(() => {
    getMinifiedPermissions().then((response) => {
      setPermissionOptions(
        response.map((item) => ({ label: item.name, value: item.url }))
      );
    });
  }, []);

  if (loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
      </Row>
    );
  }

  return (
    <Form>
      <Row>
        <Col sm={12} lg={6}>
          <Form.Group controlId="formGroupName">
            <Form.Label>
              {t("ngen.name_one")} <b style={{ color: "red" }}>*</b>
            </Form.Label>
            <Form.Control
              maxLength="150"
              value={name}
              name="name"
              isInvalid={name !== "" && !validateName(name)}
              onChange={(e) => setName(e.target.value)}
            />
            {name !== "" && !validateName(name) ? (
              <div className="invalid-feedback">{t("ngen.name.invalid")}</div>
            ) : null}
          </Form.Group>
        </Col>
      </Row>
      <Row className="mt-3">
        <Col sm={12}>
          <Form.Label>{t("w.permissions")}</Form.Label>
          <DualListBox
            key="group-permissions"
            canFilter
            options={permissionOptions}
            selected={permissions || []}
            onChange={(selected) => setPermissions(selected)}
          />
        </Col>
      </Row>
      <Row className="mt-3">
        <Col>
          <Button variant="primary" onClick={createGroup} disabled={!validateName(name)}>
            {t("button.save")}
          </Button>
          <CrudButton type="cancel" />
        </Col>
      </Row>
    </Form>
  );
};

export default FormGroup;
