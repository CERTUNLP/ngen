import React, { useState } from 'react';
import { Badge, Button, Card, CloseButton, Col, Form, Modal, Row, Spinner, Table } from 'react-bootstrap';
import CrudButton from '../../../components/Button/CrudButton';
import { Link } from 'react-router-dom';
import ModalConfirm from '../../../components/Modal/ModalConfirm';
import ButtonState from './ButtonState';
import { deleteTaxonomy, getTaxonomy } from '../../../api/services/taxonomies';
import Ordering from '../../../components/Ordering/Ordering';
import ActiveButton from '../../../components/Button/ActiveButton';
import CallBackendByName from '../../../components/CallBackendByName';
import { useTranslation } from 'react-i18next';

const TableTaxonomy = ({ setIsModify, list, loading, order, setOrder, setLoading, taxonomyGroups, minifiedTaxonomies }) => {
  const [modalDelete, setModalDelete] = useState(false);
  const [url, setUrl] = useState(null);
  const [name, setName] = useState(null);
  const [taxonomy, setTaxonomy] = useState();
  const [modalShow, setModalShow] = useState(false);
  const { t } = useTranslation();

  if (loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
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
            <Ordering
              field="created"
              label={t('date.creation')}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <Ordering
              field="name"
              label={t('ngen.name_one')}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <Ordering
              field="type"
              label={t('ngen.taxonomy.type')}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <Ordering
              field="parent__name"
              label={t('ngen.taxonomy.parent')}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <Ordering
              field="group__name"
              label={t('ngen.taxonomy.group')}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <Ordering
              field="alias_of__name"
              label={t('ngen.taxonomy.alias_of')}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <Ordering
              field="needs_review"
              label={t('ngen.taxonomy.needs_review')}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <Ordering
              field="reports"
              label={t('ngen.reports')}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <Ordering
              field="active"
              label={t('w.active')}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <th style={letterSize}>{t('ngen.options')}</th>
          </tr>
        </thead>
        <tbody>
          {list.map((taxonomy, index) => (
            <tr key={index}>
              <td>{taxonomy.created.slice(0, 10) + ' ' + taxonomy.created.slice(11, 19)}</td>
              <td>{taxonomy.name}</td>
              <td>{taxonomy.type}</td>
              <td>{minifiedTaxonomies[taxonomy.parent]}</td>
              <td>{taxonomyGroups[taxonomy.group]}</td>
              <td>{minifiedTaxonomies[taxonomy.alias_of]}</td>
              <td>{taxonomy.needs_review ? t('w.yes') : t('w.no')}</td>
              <td>{taxonomy.reports.length}</td>
              <td>
                <ButtonState taxonomy={taxonomy} />
              </td>
              <td>
                <CrudButton type="read" onClick={() => showTaxonomy(taxonomy.url)} />
                <Link to="/taxonomies/edit" state={taxonomy}>
                  <CrudButton type="edit" />
                </Link>
                <CrudButton type="delete" onClick={() => Delete(taxonomy.url, taxonomy.name)} />
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
      <Modal size="lg" show={modalShow} onHide={handleClose} aria-labelledby="contained-modal-title-vcenter" centered>
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
                      <Link to="/taxonomies/edit" state={taxonomy}>
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
                          <Form.Control plaintext readOnly defaultValue={taxonomy ? taxonomy.slug : ''} />
                        </td>
                        <td></td>
                      </tr>
                      <tr>
                        <td>{t('ngen.name_one')}</td>
                        <td>
                          <Form.Control plaintext readOnly defaultValue={taxonomy ? taxonomy.name : ''} />
                        </td>
                      </tr>
                      <tr>
                        <td>{t('w.active')}</td>
                        <td>
                          <ActiveButton active={taxonomy ? taxonomy.active : ''} />
                        </td>
                      </tr>
                      {taxonomy && taxonomy.parent && (
                        <tr>
                          <td>{t('ngen.taxonomy.parent')}</td>
                          <td>
                            {/*<p>{taxonomy.parent}</p>*/}
                            <CallBackendByName url={taxonomy.parent} callback={callbackTaxonomy} />
                          </td>
                        </tr>
                      )}
                      {taxonomy && taxonomy.group && (
                        <tr>
                          <td>{t('ngen.taxonomy.group')}</td>
                          <td>
                            <Form.Control plaintext readOnly defaultValue={taxonomy ? taxonomyGroups[taxonomy.group] : ''} />
                          </td>
                        </tr>
                      )}
                      {taxonomy && taxonomy.alias_of && (
                        <tr>
                          <td>{t('ngen.taxonomy.alias_of')}</td>
                          <td>
                            <Form.Control plaintext readOnly defaultValue={taxonomy ? minifiedTaxonomies[taxonomy.alias_of] : ''} />
                          </td>
                        </tr>
                      )}
                      <tr>
                        <td>{t('ngen.taxonomy.needs_review')}</td>
                        <td>
                          <Form.Control
                            plaintext
                            readOnly
                            defaultValue={taxonomy ? (taxonomy.needs_review ? t('w.yes') : t('w.no')) : ''}
                          />
                        </td>
                      </tr>
                      <tr>
                        <td>{t('ngen.type')}</td>
                        <td>
                          <Form.Control plaintext readOnly defaultValue={taxonomy ? taxonomy.type : ''} />
                        </td>
                      </tr>
                      {taxonomy && Boolean(taxonomy.description) && (
                        <tr>
                          <td>{t('ngen.description')}</td>
                          <td>
                            <Form.Control
                              style={{ resize: 'none' }}
                              as="textarea"
                              rows={3}
                              plaintext
                              readOnly
                              defaultValue={taxonomy.description}
                            />
                          </td>
                        </tr>
                      )}
                      <tr>
                        <td>{t('ngen.reports')}</td>
                        <td>
                          <Button size="sm" variant="light" className="text-capitalize">
                            {t('ngen.reports')}
                            <Badge variant="light" className="ml-1">
                              {taxonomy ? taxonomy.reports.length : ''}
                            </Badge>
                          </Button>
                        </td>
                      </tr>
                      <tr>
                        <td>{t('ngen.date.created')}</td>
                        <td>
                          <Form.Control
                            plaintext
                            readOnly
                            defaultValue={taxonomy ? taxonomy.created.slice(0, 10) + ' ' + taxonomy.created.slice(11, 19) : ''}
                          />
                        </td>
                      </tr>
                      <tr>
                        <td>{t('ngen.date.modified')}</td>
                        <td>
                          <Form.Control
                            plaintext
                            readOnly
                            defaultValue={taxonomy ? taxonomy.modified.slice(0, 10) + ' ' + taxonomy.modified.slice(11, 19) : ''}
                          />
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

      <ModalConfirm
        type="delete"
        component={t('ngen.taxonomy_one')}
        name={name}
        showModal={modalDelete}
        onHide={() => setModalDelete(false)}
        ifConfirm={() => removeTaxonomy(url, name)}
      />
    </React.Fragment>
  );
};

export default TableTaxonomy;
