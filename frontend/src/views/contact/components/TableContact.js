import React, { useState } from 'react';
import { Badge, Button, Card, CloseButton, Col, Form, Modal, Row, Spinner, Table } from 'react-bootstrap';
import CrudButton from '../../../components/Button/CrudButton';
import { deleteContact, getContact } from '../../../api/services/contacts';
import { Link } from 'react-router-dom';
import ModalConfirm from '../../../components/Modal/ModalConfirm';
import PriorityButton from '../../../components/Button/PriorityButton';
import Ordering from '../../../components/Ordering/Ordering';
import { useTranslation } from 'react-i18next';

const TableContact = ({ setIsModify, list, loading, setLoading, currentPage, order, setOrder }) => {
  const [contact, setContact] = useState('')

  const [modalShow, setModalShow] = useState(false)
  const [modalDelete, setModalDelete] = useState(false)
  const [url, setUrl] = useState('')
  const [id, setId] = useState('')
  const [name, setName] = useState('');
  const [created, setCreated] = useState('')
  const [modified, setModified] = useState('')
  const [type, setType] = useState('')
  const [role, setRole] = useState('')
  const { t } = useTranslation();

  if (loading) {
    return (
      <Row className='justify-content-md-center'>
        <Spinner animation='border' variant='primary' size='sm'/>
      </Row>
    );
  }

  //Read Contact
  const showContact = (url) => {
    setId(url.split('/')[(url.split('/')).length - 2]);
    setUrl(url)
    setContact('')
    getContact(url).then((response) => {
      setContact(response.data)
      let datetime = response.data.created.split('T')
      setCreated(datetime[0] + ' ' + datetime[1].slice(0, 8))
      datetime = response.data.modified.split('T');
      setModified(datetime[0] + ' ' + datetime[1].slice(0, 8))
      let rol = labelRole[response.data.role];
      setRole(rol)
      let type = labelContact[response.data.type];
      setType(type)
      setModalShow(true)
    }).catch(console.log);
  };

  //Remove Contact
  const Delete = (url, name) => {
    setUrl(url);
    setName(name);
    setModalDelete(true)
  }

  const removeContact = (url, name) => {
    deleteContact(url, name).then((response) => {
      setIsModify(response)
    }).catch((error) => {
      console.log(error)
    }).finally(() => {
      setModalDelete(false)
    })
  };

  const labelRole =
    {
      technical: `${t('ngen.role.technical')}`,
      administrative: `${t('ngen.role.administrative')}`,
      abuse: `${t('ngen.role.abuse')}`,
      notifications: `${t('ngen.role.notifications')}`,
      noc: `${t('ngen.role.noc')}`,
    };

  const labelContact =
    {
      email: 'Correo electrónico',
      telegram: 'Telegram',
      phone: 'Teléfono',
      uri: 'URI',
    };

  const storageContactUrl = (url) => {
    localStorage.setItem('contact', url);
  }

  const letterSize = { fontSize: '1.1em' }

  return (
    <React.Fragment>
      <Table responsive hover className="text-center">
        <thead>
        <tr>
          <Ordering field="name" label={t('ngen.name_one')} order={order} setOrder={setOrder} setLoading={setLoading}
                    letterSize={letterSize}/>
          <th>{t('ngen.role_one')}</th>
          <th>{t('ngen.contact_other')}</th>
          <th>{t('ngen.priority_one')}</th>
          <th>{t('ngen.action_one')}</th>
        </tr>
        </thead>
        <tbody>
        {list.map((contact, index) => {
          return (
            <tr key={contact.url}>
              <td>{contact.name}</td>
              <td>{labelRole[contact.role]}</td>
              <td>{contact.username}</td>
              <td><PriorityButton url={contact.priority}/></td>
              <td>
                <CrudButton type='read' onClick={() => showContact(contact.url)}/>
                <Link to={{ pathname: '/contacts/edit', state: contact }}>
                  <CrudButton type='edit' onClick={() => storageContactUrl(contact.url)}/>
                </Link>
                <CrudButton type='delete' onClick={() => Delete(contact.url, contact.name)}/>
              </td>
            </tr>
          );
        })}
        </tbody>
      </Table>

      <Modal size='lg' show={modalShow} onHide={() => setModalShow(false)}
             aria-labelledby="contained-modal-title-vcenter" centered>
        <Modal.Body>
          <Row>
            <Col>
              <Card>
                <Card.Header>
                  <Row>
                    <Col>
                      <Card.Title as="h5">{t('ngen.contact_other')}</Card.Title>
                      <span className="d-block m-t-5">{t('ngen.contact.detail')}</span>
                    </Col>
                    <Col sm={2} lg={2}>
                      <Link to={{ pathname: '/contacts/edit', state: contact }}>
                        <CrudButton type='edit'/>
                      </Link>
                      <CloseButton aria-label={t('w.close')} onClick={() => setModalShow(false)}/>
                    </Col>
                  </Row>
                </Card.Header>
                <Card.Body>
                  <Table responsive>
                    <tbody>
                    <tr>
                      <td>{t('ngen.system.id')}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={id}/>
                      </td>
                    </tr>
                    <tr>
                      <td>{t('ngen.name_one')}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={contact.name}/>
                      </td>
                    </tr>
                    <tr>
                      <td>{t('ngen.role_one')}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={role}/>
                      </td>
                    </tr>
                    <tr>
                      <td>{type}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={contact.username}/>
                      </td>
                    </tr>
                    {contact.public_key ?
                      <tr>
                        <td>{t('ngen.public.key')}</td>
                        <td>
                          <Form.Control plaintext readOnly defaultValue={contact.public_key}/>
                        </td>
                      </tr>
                      :
                      <></>
                    }
                    <tr>
                      <td>{t('info.related')}</td>
                      <td>
                        <Button size="sm" variant='light' className="text-capitalize">
                          Redes
                          <Badge variant="light" className="ml-2">4</Badge>
                        </Button>
                        <Button size="sm" variant='light' className="text-capitalize">
                          {t('ngen.priority_one')}
                          <PriorityButton url={contact.priority}/>
                        </Button>
                      </td>
                    </tr>
                    <tr>
                      <td>{t('ngen.date.created')}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={created}/>
                      </td>
                    </tr>
                    <tr>
                      <td>{t('ngen.date.modified')}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={modified}/>
                      </td>
                    </tr>
                    </tbody>
                  </Table>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Modal.Body>
      </Modal>
      <ModalConfirm type='delete' component='Contacto' name={name} showModal={modalDelete}
                    onHide={() => setModalDelete(false)} ifConfirm={() => removeContact(url, name)}/>
    </React.Fragment>
  );
};

export default TableContact;
