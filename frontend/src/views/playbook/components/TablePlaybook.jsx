import React, { useState } from "react";
import { Row, Spinner, Table } from "react-bootstrap";
import CrudButton from "../../../components/Button/CrudButton";
import { deletePlaybook, getPlaybook } from "../../../api/services/playbooks";
import { Link } from "react-router-dom";
import ModalConfirm from "../../../components/Modal/ModalConfirm";
import ModalDetailPlaybook from "./ModalDetailPlaybook";
import Alert from "../../../components/Alert/Alert";
import { useTranslation } from "react-i18next";

const TablePlaybook = ({ setIsModify, list, loading, taxonomyNames }) => {
  const [playbook, setPlaybook] = useState("");

  const [modalDelete, setModalDelete] = useState(false);
  const [modalShow, setModalShow] = useState(false);

  const [url, setUrl] = useState(null);
  const [name, setName] = useState(null);
  const { t } = useTranslation();

  //Alert
  const [showAlert, setShowAlert] = useState(false);

  if (loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
      </Row>
    );
  }

  //Read Playbook
  const showPlaybook = (url) => {
    setUrl(url);
    setPlaybook("");
    getPlaybook(url)
      .then((response) => {
        setPlaybook(response.data);
        setModalShow(true);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  //Remove Playbook
  const Delete = (url, name) => {
    setUrl(url);
    setName(name);
    setModalDelete(true);
  };

  const removePlaybook = (url, name) => {
    deletePlaybook(url, name)
      .then((response) => {
        setIsModify(response);
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        //ver si funciona bien
        setModalDelete(false);
        setShowAlert(true);
      });
  };

  return (
    <React.Fragment>
      <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="playbook" />
      <Table responsive hover className="text-center">
        <thead>
          <tr>
            <th>{t("ngen.name_one")}</th>
            <th>{t("ngen.taxonomy_one")}</th>
            <th>{t("ngen.action_one")}</th>
          </tr>
        </thead>
        <tbody>
          {list.map((book, index) => {
            const parts = book.url.split("/");
            let itemNumber = parts[parts.length - 2];
            return (
              <tr key={index}>
                <td>{book.name}</td>
                <td>
                  {book.taxonomy.map((taxonomy, tindex) => {
                    return <li key={tindex}>{taxonomyNames[taxonomy]}</li>;
                  })}
                </td>
                <td>
                  <CrudButton type="read" onClick={() => showPlaybook(book.url)} />
                  <Link to={`/playbooks/edit/${itemNumber}`}>
                    <CrudButton type="edit" />
                  </Link>
                  <CrudButton type="delete" onClick={() => Delete(book.url, book.name)} />
                </td>
              </tr>
            );
          })}
        </tbody>
      </Table>
      <ModalDetailPlaybook show={modalShow} playbook={playbook} onHide={() => setModalShow(false)} />
      <ModalConfirm
        type="delete"
        component="Playbook"
        name={name}
        showModal={modalDelete}
        onHide={() => setModalDelete(false)}
        ifConfirm={() => removePlaybook(url, name)}
      />
    </React.Fragment>
  );
};

export default TablePlaybook;
