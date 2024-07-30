import React, { useState } from 'react';
import { Row, Table, Spinner, Modal, Col, Card, CloseButton, Button, Badge, Form } from 'react-bootstrap';
import CrudButton from '../../../components/Button/CrudButton';
import { Link } from 'react-router-dom';
import ModalConfirm from '../../../components/Modal/ModalConfirm';
import ButtonView from './ButtonView';
import ButtonState from './ButtonState';
import { deleteTaxonomy, getTaxonomy } from '../../../api/services/taxonomies';
import Ordering from '../../../components/Ordering/Ordering';
import ActiveButton from '../../../components/Button/ActiveButton';
import CallBackendByName from '../../../components/CallBackendByName';
import { useTranslation, Trans } from 'react-i18next';

const TableTaxonomy = ({ setIsModify, list, loading, order, setOrder, setLoading }) => {
  const [modalDelete, setModalDelete] = useState(false);
  const [url, setUrl] = useState(null);
  const [name, setName] = useState(null);
  const [taxonomy, setTaxonomy] = useState();
  const [modalShow, setModalShow] = useState(false);
  const [created, setCreated] = useState(null);
  const [modified, setModified] = useState(null);
  const { t } = useTranslation();

  if (loading) {
    return (
      <Row className='justify-content-md-center'>
        <Spinner animation='border' variant='primary' size='sm' />
      </Row>
    );
  }

  const handleClose = () => setModalShow(false);

  const Delete = (url, name) => {
    setUrl(url);
    setName(name);
    setModalDelete(true);
  };

  const showTaxonomy = (url) => {
    getTaxonomy(url)
      .then((response) => {
        setTaxonomy(response.data);
        let datetime = response.data.created.split('T');
        setCreated(datetime[0] + ' ' + datetime[1].slice(0, 8));
        datetime = response.data.modified.split('T');
        setModified(datetime[0] + ' ' + datetime[1].slice(0, 8));
        setModalShow(true);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  const removeTaxonomy = (url, name) => {
    deleteTaxonomy(url, name)
      .then((response) => {
        setIsModify(response);
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        setModalDelete(false);
      });
  };

  const callbackTaxonomy = (url, set) => {
    getTaxonomy(url)
      .then((response) => {
        console.log(response);
        set(response.data);
      })
      .catch();
  };

  const letterSize = { fontSize: '1.1em' };

  return (
    <React.Fragment>
      <Table responsive hover className="text-center">
        <thead>
          <tr>
            <Ordering field="name" label={t('ngen.name_one')} order={order} setOrder={setOrder} setLoading={setLoading} letterSize={letterSize} />
            <th style={letterSize}>{t('w.active')}</th>
            <th style={letterSize}>{t('ngen.reports')}</th>
            <th style={letterSize}>{t('ngen.options')}</th>
          </tr>
        </thead>
        <tbody>
          {list.map((taxonomy, index) => (
            <tr key={index}>
              <td>{taxonomy.name}</td>
              <td>
                <ButtonState taxonomy={taxonomy} />
              </td>
              <td>{taxonomy.reports.length}</td>
              <td>
                <CrudButton type='read' onClick={() => showTaxonomy(taxonomy.url)} />
                <Link to={{ pathname: "./taxonomies/edit", state: taxonomy }}>
                  <CrudButton type="edit" />
                </Link>
                <CrudButton type='delete' onClick={() => Delete(taxonomy.url, taxonomy.name)} />
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
      <Modal size='lg' show={modalShow} onHide={handleClose} aria-labelledby="contained-modal-title-vcenter" centered>
        <Modal.Body>
          <Row>
            <Col>
              <Card>
                <Card.Header>
                  <Row>
                    <Col>
                      <Card.Title as="h5">{t('ngen.taxonomy_one')}</Card.Title>
                      <span className="d-block m-t-5">{t('ngen.taxonomy.detail')}</span>
                    </Col>
                    <Col sm={12} lg={2}>
                      <Link to={{ pathname: "./taxonomy/edit", state: taxonomy }}>
                        <CrudButton type="edit" />
                      </Link>
                      <CloseButton aria-label={t('w.close')} onClick={handleClose} />
                    </Col>
                  </Row>
                </Card.Header>
                <Card.Body>
                  <Table responsive>
                    <tbody>
                      <tr>
                        <td>{t('ngen.system.id')}</td>
                        <td>
                          <Form.Control plaintext readOnly defaultValue={taxonomy ? taxonomy.slug : ""} />
                        </td>
                        <td></td>
                      </tr>
                      <tr>
                        <td>{t('ngen.name_one')}</td>
                        <td>
                          <Form.Control plaintext readOnly defaultValue={taxonomy ? taxonomy.name : ""} />
                        </td>
                      </tr>
                      <tr>
                        <td>{t('w.active')}</td>
                        <td>
                          <ActiveButton active={taxonomy ? taxonomy.active : ""} />
                        </td>
                      </tr>
                      <tr>
                        <td>{t('ngen.type')}</td>
                        <td>
                          <Form.Control plaintext readOnly defaultValue={taxonomy ? taxonomy.type : ""} />
                        </td>
                      </tr>
                      {taxonomy && taxonomy.description && (
                        <tr>
                          <td>{t('ngen.description')}</td>
                          <td>
                            <Form.Control style={{ resize: "none" }} as="textarea" rows={3} plaintext readOnly defaultValue={taxonomy.description} />
                          </td>
                        </tr>
                      )}
                      {taxonomy && taxonomy.parent && (
                        <tr>
                          <td>Padre</td>
                          <td>
                            <CallBackendByName url={taxonomy.parent} callback={callbackTaxonomy} />
                          </td>
                        </tr>
                      )}
                      <tr>
                        <td>{t('ngen.reports')}</td>
                        <td>
                          <Button size="sm" variant='light' className="text-capitalize">
                            {t('ngen.reports')}
                            <Badge variant="light" className="ml-1">{taxonomy ? taxonomy.reports.length : ""}</Badge>
                          </Button>
                        </td>
                      </tr>
                      <tr>
                        <td>{t('w.creation')}</td>
                        <td>
                          <Form.Control plaintext readOnly defaultValue={taxonomy ? taxonomy.created.slice(0, 10) + " " + taxonomy.created.slice(11, 19) : ""} />
                        </td>
                      </tr>
                      <tr>
                        <td>{t('w.update')}</td>
                        <td>
                          <Form.Control plaintext readOnly defaultValue={taxonomy ? taxonomy.modified.slice(0, 10) + " " + taxonomy.modified.slice(11, 19) : ""} />
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

      <ModalConfirm type='delete' component={t('ngen.taxonomy_one')} name={name} showModal={modalDelete} onHide={() => setModalDelete(false)} ifConfirm={() => removeTaxonomy(url, name)} />
    </React.Fragment>
  );
};

export default TableTaxonomy;

