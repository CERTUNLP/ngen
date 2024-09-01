import React, { useEffect, useState } from 'react'
import { useLocation, useParams } from 'react-router-dom';
import { Card, Col, Row } from 'react-bootstrap'
import { getAllContacts } from '../../api/services/contacts'
import { putNetwork, getNetwork } from '../../api/services/networks'
import FormCreateNetwork from './components/FormCreateNetwork'
import Navigation from '../../components/Navigation/Navigation'
import Alert from '../../components/Alert/Alert'
import { useTranslation } from 'react-i18next'
import { COMPONENT_URL } from 'config/constant';

const EditNetwork = () => {

  const [network, setNetwork] = useState({})
  const [id] = useState(useParams());
  const { t } = useTranslation()

  const [url, setUrl] = useState("")
  const [children, setChildren] = useState("")
  const [cidr, setCidr] = useState("") //*
  const [domain, setDomain] = useState("") // null
  const [active, setActive] = useState() //* true
  const [address_value, setAddress_value] = useState() //* true
  const [type, setType] = useState() //* internal external
  const [parent, setParent] = useState("")
  const [network_entity, setNetwork_entity] = useState("")
  const [contacts, setContacts] = useState() //*

  //Dropdown
  const [contactsOption, setContactsOption] = useState([]);
  const [contactCreated, setContactsCreated] = useState(null); // si creo se renderiza

  //Alert
  const [showAlert, setShowAlert] = useState(false);

  useEffect(() => {

    if (id.id) {
      getNetwork(COMPONENT_URL.network + id.id + "/")
        .then((response) => {
          setNetwork(response.data)
        }).catch(error => console.log(error));

    }
  }, [id]);

  useEffect(() => {

    if (network) {
      setUrl(network.url)
      setChildren(network.children)
      setCidr(network.cidr === null ? '' : network.cidr) //*
      setDomain(network.domain) // null
      setActive(network.active) //* true
      setAddress_value(network.address_value) //* true
      setType(network.type) //* internal external
      setParent(network.parent)
      setNetwork_entity(network.network_entity)
      setContacts(network.contacts) //*
    }
  }, [network]);

  useEffect(() => {
    //multiselect all options
    getAllContacts()
      .then((response) => {
        let listContact = response.map((contactsItem) => {
          return {
            value: contactsItem.url,
            label: contactsItem.name + " (" + labelRole[contactsItem.role] + ") " + contactsItem.username
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

  //Update
  const editNetwork = () => {
    putNetwork(url, children, active, type, parent, network_entity, contacts,address_value)
      .then((response) => {
        window.location.href = '/networks'
      }).catch((error) => {
        setShowAlert(true)
        console.log(error)
      })
  }

  return (
    <React.Fragment>
      <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="network" />
      <Row>
        <Navigation actualPosition={t('ngen.network.edit')} path="/networks" index={t('ngen.network_other')} />
      </Row>
      <Row>
        <Col sm={12}>
          <Card>
            <Card.Header>
              <Row>
                <Col>
                  <Card.Title as="h5">{t("ngen.network_other")}</Card.Title>
                  <span className="d-block m-t-5">{t("ngen.network.edit")}</span>
                </Col>
              </Row>
            </Card.Header>
            <Card.Body>
              {network.url ? <FormCreateNetwork
                cidr={cidr} setCidr={setCidr}
                domain={domain} setDomain={setDomain}
                type={type} setType={setType}
                parent={parent} setParent={setParent}
                network_entity={network_entity}
                setNetwork_entity={setNetwork_entity}
                address_value={address_value}
                setAddress_value={setAddress_value}
                active={active}
                setActive={setActive}
                ifConfirm={editNetwork}
                edit={true}
                contacts={contacts}
                setContacts={setContacts}
                allContacts={contactsOption}
                setContactsCreated={setContactsCreated} />
                : ""
              }

            </Card.Body>
          </Card>
        </Col>
      </Row>
    </React.Fragment>
  );
};

export default EditNetwork;
