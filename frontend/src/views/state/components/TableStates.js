import React, { useState } from 'react'
import { Button, Card, CloseButton, Col, Form, Modal, Row, Spinner, Table } from 'react-bootstrap';
import CrudButton from '../../../components/Button/CrudButton';
import { Link } from 'react-router-dom'
import ActiveButton from '../../../components/Button/ActiveButton';
import ModalConfirm from '../../../components/Modal/ModalConfirm';
import { deleteState, getState, isActive } from "../../../api/services/states";
import Alert from '../../../components/Alert/Alert';
import CallBackendByName from '../../../components/CallBackendByName';
import { useTranslation } from 'react-i18next';

const TableStates = ({ states, callback, loading, currentPage }) => {
  const [deleteName, setDeleteName] = useState()
  const [deleteUrl, setDeleteUrl] = useState()
  const [remove, setRemove] = useState()
  const [dataState, setDataState] = useState({})
  const [showState, setShowState] = useState()
  const [state, setState] = useState({});
  const [modalShow, setModalShow] = useState(false);
  const [showAlert, setShowAlert] = useState(false)
  const { t } = useTranslation();

  if (loading) {
    return (
      <Row className='justify-content-md-center'>
        <Spinner animation='border' variant='primary' size='sm'/>
      </Row>
    );
  }

  const modalDelete = (name, url) => {
    setDeleteName(name)
    setDeleteUrl(url)
    setRemove(true)

  }
  const handleDelete = () => {
    deleteState(deleteUrl, deleteName).then(() => {
      window.location.href = '/states';
    }).catch((error) => {
      setShowAlert(true)
      console.log(error)
    }).finally(() => {
      setRemove(false)
    })
  }
  const modalChangeState = (url, name, active) => {

    setDataState({ url: url, name: name, state: active })
    setShowState(true)
  }
  const callbackState = (url, setPriority) => {
    getState(url).then((response) => {
      console.log(response)
      setPriority(response.data)
    }).catch();
  }
  const changeState = () => {

    isActive(dataState.url, +!dataState.state).then(() => {
      window.location.href = '/states';
    }).catch((error) => {
      setShowAlert(true)
      console.log(error)
    }).finally(() => {
      setShowState(false)
    })
  }
  const showModalState = (state) => {
    setState(state)
    setModalShow(true)
  }
  const resetShowAlert = () => {
    setShowAlert(false);
  }


  return (
    <div>
      <Alert showAlert={showAlert} resetShowAlert={resetShowAlert}/>

      <ul className="list-group my-4">
        <Table responsive hover className="text-center">
          <thead>
          <tr>
            <th>{t('ngen.name_one')}</th>
            <th>{t('ngen.state_one')}</th>
            <th>{t('w.attended')}</th>
            <th>{t('w.solved')}</th>
            <th>{t('ngen.options')}</th>
          </tr>
          </thead>
          <tbody>
          {states.map((state, index) => {
            return (
              <tr key={index}>
                <td>{state.name}</td>
                <td>
                  <ActiveButton active={state.active}
                                onClick={() => modalChangeState(state.url, state.name, state.active)}/>
                </td>
                <td>{state.attended ? t('ngen.true') : t('ngen.false')}</td>

                <td>{state.solved ? t('ngen.true') : t('ngen.false')}</td>


                <td>
                  <CrudButton type='read' onClick={() => showModalState(state)}/>
                  <Link to={{ pathname: "/states/edit", state: state }}>
                    <CrudButton type='edit'/>
                  </Link>
                  <CrudButton type='delete' onClick={() => modalDelete(state.name, state.url)}/>
                </td>
              </tr>
            )
          })}

          <ModalConfirm type='delete' component={t('ngen.state_one')} name={deleteName} showModal={remove}
                        onHide={() => setRemove(false)} ifConfirm={() => handleDelete(deleteUrl)}/>
          <ModalConfirm type='editState' component={t('ngen.state_one')} name={dataState.name} state={dataState.state}
                        showModal={showState} onHide={() => setShowState(false)} ifConfirm={() => changeState()}/>
          <Modal size='lg' show={modalShow} onHide={() => setModalShow(false)}
                 aria-labelledby="contained-modal-title-vcenter" centered>
            <Modal.Body>
              <Row>
                <Col>
                  <Card>
                    <Card.Header>
                      <Row>
                        <Col>
                          <Card.Title as="h5">{t('ngen.state_one')}</Card.Title>
                          <span className="d-block m-t-5">{t('ngen.state.detail')}</span>
                        </Col>
                        <Col sm={12} lg={4}>
                          <Link to={{ pathname: "/states/edit", state: state }}>
                            <CrudButton type='edit'/>
                          </Link>
                          <CloseButton aria-label={t('w.close')} onClick={() => setModalShow(false)}/>
                        </Col>
                      </Row>
                    </Card.Header>
                    <Card.Body>
                      <Table responsive>
                        <tr>
                          <td>{t('ngen.name_one')}</td>
                          <td>
                            <Form.Control plaintext readOnly defaultValue={state.name}/>
                          </td>
                          <td></td>
                        </tr>
                        <tr>
                          <td>{t('w.attended')}</td>
                          <td>
                            <Form.Control plaintext readOnly defaultValue={state.attended}/>
                          </td>
                        </tr>
                        <tr>
                          <td>{t('w.solved')}</td>
                          <td>
                            <Form.Control plaintext readOnly defaultValue={state.solved}/>
                          </td>
                        </tr>

                        <tr>
                          <td>activo</td>
                          <td>
                            <Button
                              className="btn-icon btn-rounded"
                              variant={state.active ? 'outline-success' : 'outline-danger'}
                              title={state.active ? 'Activo' : 'Inactivo'}>
                              <i
                                className={state.active ? 'feather icon-check-circle' : 'feather icon-alert-triangle'}/>
                            </Button>
                          </td>
                        </tr>
                        <tr>
                          <td>{t('ngen.description')}</td>
                          <td>
                            <Form.Control plaintext readOnly defaultValue={state.description}/>
                          </td>
                        </tr>
                        <tr>
                          <td>{t('ngen.children')}</td>
                          <td>
                            {
                              state.children ? state.children.map((url) => {
                                  console.log(url)
                                  return (<CallBackendByName url={url} callback={callbackState} useBadge={false}/>)
                                })

                                : "No tiene hijos"
                            }
                          </td>
                        </tr>
                        <tr>
                          <td>{t('ngen.date.created')}</td>
                          <td>
                            <Form.Control plaintext readOnly
                                          defaultValue={state.created ? state.created.slice(0, 10) + " " + state.created.slice(11, 19) : ""}/>
                          </td>
                        </tr>
                        <tr>
                          <td>{t('ngen.date.modified')}</td>
                          <td>
                            <Form.Control plaintext readOnly
                                          defaultValue={state.modified ? state.modified.slice(0, 10) + " " + state.modified.slice(11, 19) : ""}/>
                          </td>
                        </tr>

                      </Table>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
            </Modal.Body>
          </Modal>

          </tbody>
        </Table>
      </ul>

    </div>
  )
}

export default TableStates
