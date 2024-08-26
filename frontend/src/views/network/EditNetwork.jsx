import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Card, Col, Row } from 'react-bootstrap';
import { getAllContacts } from '../../api/services/contacts';
import { putNetwork } from '../../api/services/networks';
import FormCreateNetwork from './components/FormCreateNetwork';
import Navigation from '../../components/Navigation/Navigation';
import Alert from '../../components/Alert/Alert';
import { useTranslation } from 'react-i18next';

const EditNetwork = () => {
  const location = useLocation();
  const fromState = location.state;
  const [network] = useState(fromState);
  const { t } = useTranslation();

  const [url] = useState(network.url);
  const [children] = useState(network.children);
  const [cidr, setCidr] = useState(network.cidr === null ? '' : network.cidr); //*
  const [domain, setDomain] = useState(network.domain); // null
  const [active, setActive] = useState(network.active); //* true
  const [address_value, setAddress_value] = useState(network.address_value); //* true
  const [type, setType] = useState(network.type); //* internal external
  const [parent, setParent] = useState(network.parent);
  const [network_entity, setNetwork_entity] = useState(network.network_entity);
  const [contacts, setContacts] = useState(network.contacts); //*

  //Dropdown
  const [contactsOption, setContactsOption] = useState([]);
  const [contactCreated, setContactsCreated] = useState(null); // si creo se renderiza

  //Alert
  const [showAlert, setShowAlert] = useState(false);

  useEffect(() => {
    //multiselect all options
    getAllContacts()
      .then((response) => {
        let listContact = response.map((contactsItem) => {
          return {
            value: contactsItem.url,
            label: contactsItem.name + ' (' + labelRole[contactsItem.role] + ') ' + contactsItem.username
          };
        });
        setContactsOption(listContact);
      })
      .catch((error) => {
        console.log(error);
      });
  }, [contactCreated]);

  const labelRole = {
    technical: `${t('ngen.role.technical')}`,
    administrative: `${t('ngen.role.administrative')}`,
    abuse: `${t('ngen.role.abuse')}`,
    notifications: `${t('ngen.role.notifications')}`,
    noc: `${t('ngen.role.noc')}`
  };

  //Update
  const editNetwork = () => {
    putNetwork(url, children, active, type, parent, network_entity, contacts, address_value)
      .then((response) => {
        window.location.href = '/networks';
      })
      .catch((error) => {
        setShowAlert(true);
        console.log(error);
      });
  };

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
                  <Card.Title as="h5">{t('ngen.network_other')}</Card.Title>
                  <span className="d-block m-t-5">{t('ngen.network.edit')}</span>
                </Col>
              </Row>
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
                active={active}
                setActive={setActive}
                ifConfirm={editNetwork}
                edit={true}
                contacts={contacts}
                setContacts={setContacts}
                allContacts={contactsOption}
                setContactsCreated={setContactsCreated}
              />
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </React.Fragment>
  );
};

export default EditNetwork;
