import React, { useEffect, useState } from "react";
import { Card, Col, Row } from "react-bootstrap";
import { getAllContacts } from "../../api/services/contacts";
import { postNetwork } from "../../api/services/networks";
import FormCreateNetwork from "./components/FormCreateNetwork";
import Navigation from "../../components/Navigation/Navigation";
import Alert from "../../components/Alert/Alert";
import { useTranslation } from "react-i18next";

const CreateNetwork = () => {
  const [cidr, setCidr] = useState(""); //required
  const [type, setType] = useState(""); //required
  const [contacts, setContacts] = useState([]); //required
  const active = true; //required: true
  const children = useState(null); //?
  const [domain, setDomain] = useState(null); // null
  const [parent, setParent] = useState(null);
  const [network_entity, setNetwork_entity] = useState(null);
  const [address_value, setAddress_value] = useState("");
  const { t } = useTranslation();

  //Dropdown
  const [contactsOption, setContactsOption] = useState([]);
  const [contactCreated, setContactsCreated] = useState(null); // si creo se renderiza

  //Alert
  const [showAlert, setShowAlert] = useState(false);

  useEffect(() => {
    getAllContacts()
      .then((response) => {
        let listContact = response.map((contactsItem) => {
          return {
            value: contactsItem.url,
            label: contactsItem.name + " (" + labelRole[contactsItem.role] + ")"
          };
        });
        setContactsOption(listContact);
      })
      .catch((error) => {
        console.log(error);
      });
  }, [contactCreated]);

  const labelRole = {
    technical: `${t("ngen.role.technical")}`,
    administrative: `${t("ngen.role.administrative")}`,
    abuse: `${t("ngen.role.abuse")}`,
    notifications: `${t("ngen.role.notifications")}`,
    noc: `${t("ngen.role.noc")}`
  };

  const createNetwork = () => {
    postNetwork(children, active, type, parent, network_entity, contacts, address_value)
      .then((response) => {
        window.location.href = "/networks";
      })
      .catch(() => {
        setShowAlert(true);
      });
  };

  return (
    <React.Fragment>
      <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="network" />
      <Row>
        <Navigation actualPosition={t("ngen.network.create")} path="/networks" index={t("ngen.network_other")} />
      </Row>
      <Row>
        <Col sm={12}>
          <Card>
            <Card.Header>
              <Card.Title as="h5">{t("ngen.network_other")}</Card.Title>
              <span className="d-block m-t-5">
                {t("crud.add")} {t("ngen.network_one")}
              </span>
            </Card.Header>
            <Card.Body>
              <FormCreateNetwork
                cidr={cidr}
                setCidr={setCidr}
                domain={domain}
                setDomain={setDomain}
                type={type}
                setType={setType}
                parent={parent}
                setParent={setParent}
                network_entity={network_entity}
                setNetwork_entity={setNetwork_entity}
                address_value={address_value}
                setAddress_value={setAddress_value}
                contacts={contacts}
                setContacts={setContacts}
                ifConfirm={createNetwork}
                edit={false}
                allContacts={contactsOption}
                setContactsCreated={setContactsCreated}
                setShowAlert={setShowAlert}
              />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </React.Fragment>
  );
};

export default CreateNetwork;
