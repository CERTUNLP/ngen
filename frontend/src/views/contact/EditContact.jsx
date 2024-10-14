import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, Col, Row } from "react-bootstrap";
import Alert from "../../components/Alert/Alert";
import { getContact, patchContact } from "../../api/services/contacts";
import FormCreateContact from "./components/FormCreateContact";
import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { COMPONENT_URL } from "config/constant";

const EditContact = () => {
  const [contact, setContact] = useState({});
  const navigate = useNavigate();
  const { t } = useTranslation();

  const [supportedName, setSupportedName] = useState("");
  const [selectRol, setSelectRol] = useState("");
  const [supportedPriority, setSupportedPriority] = useState("");
  const [supportedContact, setSupportedContact] = useState("");
  const [supportedKey, setSupportedKey] = useState("");
  const [networks, setNetworks] = useState([]);
  const [selectType, setSelectType] = useState("");
  const [id] = useState(useParams());
  const [user, setUser] = useState("");

  //Alert
  const [showAlert, setShowAlert] = useState(false);

  useEffect(() => {
    if (id.id) {
      getContact(COMPONENT_URL.contact + id.id + "/")
        .then((response) => {
          setContact(response.data);
        })
        .catch((error) => console.log(error));
    }
  }, [id]);

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
    patchContact(contact.url, supportedName, supportedContact, supportedKey, selectType, selectRol, supportedPriority, user)
      .then((response) => {})
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
