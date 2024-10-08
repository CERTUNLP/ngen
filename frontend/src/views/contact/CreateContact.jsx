import React, { useState } from "react";
import { Card, Col, Row } from "react-bootstrap";
import { postContact } from "../../api/services/contacts";
import FormCreateContact from "./components/FormCreateContact";
import Alert from "../../components/Alert/Alert";
import { useTranslation } from "react-i18next";

const CreateContact = () => {
  const [supportedName, setSupportedName] = useState("");
  const [selectRol, setSelectRol] = useState("");
  const [supportedPriority, setSupportedPriority] = useState("");
  const [supportedContact, setSupportedContact] = useState("");
  const [supportedKey, setSupportedKey] = useState(null);
  const [networks, setNetworks] = useState([]);
  const [selectType, setSelectType] = useState("");
  const [user, setUser] = useState("");
  const { t } = useTranslation();

  //Alert
  const [showAlert, setShowAlert] = useState(false);

  const createContact = () => {
    //refactorizar al FormCreateContact

    postContact(supportedName, supportedContact, supportedKey, selectType, selectRol, supportedPriority, user, networks)
      .then((response) => {
        window.location.href = "/contacts";
      })
      .catch(() => {
        setShowAlert(true);
      });
  };

  return (
    <React.Fragment>
      <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="contact" />
      <Row>
        <Col sm={12}>
          <Card>
            <Card.Header>
              <Card.Title as="h5">{t("ngen.contact_other")}</Card.Title>
              <span className="d-block m-t-5">
                {t("w.add")} {t("ngen.contact_one")}
              </span>
            </Card.Header>
            <Card.Body>
              <FormCreateContact
                name={supportedName}
                setName={setSupportedName}
                role={selectRol}
                setRole={setSelectRol}
                priority={supportedPriority}
                setPriority={setSupportedPriority}
                user={user}
                setUser={setUser}
                type={selectType}
                setType={setSelectType}
                contact={supportedContact}
                setContact={setSupportedContact}
                keypgp={supportedKey}
                setKey={setSupportedKey}
                ifConfirm={createContact}
                ifCancel={() => (window.location.href = "/contacts")}
              />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </React.Fragment>
  );
};

export default CreateContact;
