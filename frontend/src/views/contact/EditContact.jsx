import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Card, Col, Row } from "react-bootstrap";
import Alert from "../../components/Alert/Alert";
import { getContact, putContact } from "../../api/services/contacts";
import FormCreateContact from "./components/FormCreateContact";
import Navigation from "../../components/Navigation/Navigation";
import { useTranslation } from "react-i18next";

const EditContact = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const fromState = location.state;
  const [contact, setContact] = useState(fromState);
  const { t } = useTranslation();

  const [supportedName, setSupportedName] = useState("");
  const [selectRol, setSelectRol] = useState("");
  const [supportedPriority, setSupportedPriority] = useState("");
  const [supportedContact, setSupportedContact] = useState("");
  const [supportedKey, setSupportedKey] = useState("");
  const [selectType, setSelectType] = useState("");
  const [user, setUser] = useState("");

  //Alert
  const [showAlert, setShowAlert] = useState(false);

  useEffect(() => {
    if (contact) {
      setSupportedName(contact.name);
      setSelectRol(contact.role);
      setSupportedPriority(contact.priority);
      setSupportedContact(contact.username);
      setSupportedKey(contact.public_key);
      setSelectType(contact.type);
      setUser(contact.user);
    } else {
      const contactUrl = localStorage.getItem("contact");
      getContact(contactUrl)
        .then((response) => {
          setContact(response.data);
        })
        .catch((error) => console.log(error));
    }
  }, [contact]);

  const editContact = () => {
    putContact(contact.url, supportedName, supportedContact, supportedKey, selectType, selectRol, supportedPriority, user)
      .then((response) => {
      })
      .catch(() => {
        setShowAlert(true);
      });
  };

  return (
    <React.Fragment>
      <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="contact" />
      <Row>
        <Navigation actualPosition={t("ngen.contact.edit")} path="/contacts" index={t("ngen.contact_other")} />
      </Row>
      <Row>
        <Col sm={12}>
          <Card>
            <Card.Header>
              <Card.Title as="h5">{t("ngen.contact_other")}</Card.Title>
              <span className="d-block m-t-5">
                {t("w.edit")} {t("ngen.contact_one")}
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
                ifConfirm={editContact}
                ifCancel={() => {
                  localStorage.removeItem("contact");
                  navigate(-1);
                }}
              />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </React.Fragment>
  );
};

export default EditContact;
