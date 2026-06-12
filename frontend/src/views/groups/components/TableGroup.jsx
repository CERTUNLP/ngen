import React, { useState } from "react";
import { Button, Modal, Row, Spinner, Table } from "react-bootstrap";
import { deleteGroup, getGroup } from "api/services/groups";
import { getMinifiedPermissions } from "api/services/permissions";
import CrudButton from "components/Button/CrudButton";
import ModalConfirm from "components/Modal/ModalConfirm";
import Alert from "components/Alert/Alert";
import Ordering from "components/Ordering/Ordering";
import { useTranslation } from "react-i18next";

const TableGroup = ({ groups, loading, order, setOrder, setLoading, currentPage, setIsModify }) => {
  const [remove, setRemove] = useState(false);
  const [deleteName, setDeleteName] = useState("");
  const [deleteUrl, setDeleteUrl] = useState("");
  const [modalShow, setModalShow] = useState(false);
  const [group, setGroup] = useState({});
  const [permissionNames, setPermissionNames] = useState({});
  const [showAlert, setShowAlert] = useState(false);
  const { t } = useTranslation();

  if (loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
      </Row>
    );
  }

  const handleShow = (name, url) => {
    setDeleteName(name);
    setDeleteUrl(url);
    setRemove(true);
  };

  const handleDelete = () => {
    deleteGroup(deleteUrl, deleteName)
      .then(() => {
        window.location.href = "/groups";
      })
      .catch((error) => {
        setShowAlert(true);
        console.log(error);
      })
      .finally(() => {
        setRemove(false);
      });
  };

  const showModalGroup = (groupItem) => {
    Promise.all([
      getGroup(groupItem.url),
      getMinifiedPermissions(),
    ]).then(([groupResponse, permissions]) => {
      const g = groupResponse.data;
      setGroup(g);
      if (g.permissions?.length > 0) {
        const permDict = {};
        permissions.forEach((p) => {
          permDict[p.url] = p.name;
        });
        setPermissionNames(permDict);
      }
    });
    setModalShow(true);
  };

  const resetShowAlert = () => {
    setShowAlert(false);
  };

  const letterSize = {};

  return (
    <>
      <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} component="group" />
      <Table responsive hover className="text-center">
        <thead>
          <tr>
            <Ordering
              field="name"
              label={t("ngen.name_one")}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <th style={letterSize}>{t("ngen.options")}</th>
          </tr>
        </thead>
        <tbody>
          {groups.length === 0 ? (
            <tr>
              <td colSpan={2} className="text-muted py-4">
                {t("w.no_data")}
              </td>
            </tr>
          ) : (
            groups.map((groupItem) => {
              const itemNumber = parseInt(groupItem.url.split("/").filter(Boolean).pop());
              return (
                <tr key={groupItem.url}>
                  <td>{groupItem.name}</td>
                  <td className="text-nowrap">
                    <CrudButton type="read" onClick={() => showModalGroup(groupItem)} />
                    <CrudButton type="edit" to={`/groups/edit/${itemNumber}`} checkPermRoute />
                    <CrudButton type="delete" onClick={() => handleShow(groupItem.name, groupItem.url)} permissions="delete_group" />
                  </td>
                </tr>
              );
            })
          )}
        </tbody>
      </Table>

      <ModalConfirm
        type="delete"
        component={t("w.group")}
        name={deleteName}
        showModal={remove}
        onHide={() => setRemove(false)}
        ifConfirm={handleDelete}
      />

      <Modal show={modalShow} onHide={() => setModalShow(false)} size="lg" centered>
        <Modal.Header closeButton>
          <Modal.Title>
            {t("w.group")}: {group.name}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <dl className="row mb-1">
            <dt className="col-sm-3">{t("ngen.name_one")}</dt>
            <dd className="col-sm-9">{group.name || "-"}</dd>
          </dl>
          <dl className="row mb-1">
            <dt className="col-sm-3">{t("w.permissions")}</dt>
            <dd className="col-sm-9">
              {group.permissions?.length > 0
                ? group.permissions.map((permUrl) => (
                    <span key={permUrl} className="badge bg-secondary me-1">
                      {permissionNames[permUrl] || "..."}
                    </span>
                  ))
                : "-"}
            </dd>
          </dl>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setModalShow(false)}>
            {t("w.close")}
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default TableGroup;
