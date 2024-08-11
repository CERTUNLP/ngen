import React, { useEffect, useState } from 'react';
import { Button, Card, CloseButton, Col, Collapse, Modal, Row, Table } from 'react-bootstrap';
import { getPlaybook } from '../../api/services/playbooks';
import CrudButton from '../../components/Button/CrudButton';
import FormCreateTask from './components/FormCreateTask';
import { postTask } from '../../api/services/tasks';
import RowTask from './components/RowTask';
import AdvancedPagination from '../../components/Pagination/AdvancedPagination';
import { useTranslation } from 'react-i18next';

const ListTask = (props) => { //props setAlert

  const [tasks, setTasks] = useState('')

  //Create Task
  const [modalCreate, setModalCreate] = useState(false)
  const [name, setName] = useState(''); //required
  const [priority, setPriority] = useState('0'); //required
  const [description, setDescription] = useState('');
  const { t } = useTranslation();

  const [taskCreated, setTaskCreated] = useState(null);
  const [taskDeleted, setTaskDeleted] = useState(null);
  const [taskUpdated, setTaskUpdated] = useState(null);

  const [playbook, setPlaybook] = useState(null); //required

  //AdvancedPagination
  const [currentPage, setCurrentPage] = useState(1);
  const [countItems] = useState(0);

  function updatePage(chosenPage) {
    setCurrentPage(chosenPage);
  }

  useEffect(() => {
    getPlaybook(props.urlPlaybook).then((response) => {
      setPlaybook(response.data)
      setTasks(response.data.tasks)
    }).catch((error) => {
      console.log(error)
    })
  }, [taskCreated, taskUpdated, taskDeleted, countItems, currentPage, props.urlPlaybook]) //, isModify

  const createTask = () => {
    postTask(name, description, priority, props.urlPlaybook).then((response) => {
      setTaskCreated(response)
      setName('')
      setPriority('0')
      setDescription('')
      setModalCreate(false)
    }).catch((error) => {
      console.log(error)
    }).finally(() => {
      props.setShowAlert(true)
    })
  };

  return (
    <React.Fragment>
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <Row>
                <Col sm={12} lg={9}>
                  <Card.Title as="h5">{t('ngen.tasks')}</Card.Title>
                  <span className="d-block m-t-5">{t('ngen.tasks.list')}</span>
                </Col>
                <Col sm={12} lg={3}>
                  {props.sectionAddTask ?
                    <CrudButton type='create' name={t('ngen.task')} onClick={() => setModalCreate(true)}/>
                    :
                    <><Button variant="outline-primary" disabled>{t('ngen.tasks.list')}</Button></>
                  }
                </Col>
              </Row>
            </Card.Header>

            <Collapse in={props.sectionAddTask}>
              <div id="basic-collapse">
                <Card.Body>
                  <Table responsive hover className="text-center">
                    <thead>
                    <tr>
                      <th>#</th>
                      <th>{t('ngen.name_one')}</th>
                      <th>{t('ngen.priority_one')}</th>
                      <th>{t('ngen.description')}</th>
                      <th>{t('ngen.action_one')}</th>
                    </tr>
                    </thead>
                    <tbody>
                    {console.log(tasks)}
                    {tasks ?
                      tasks.map((urlTask, index) => {
                        return (
                          <RowTask url={urlTask} id={index + 1} taskDeleted={taskDeleted}
                                   setTaskDeleted={setTaskDeleted}
                                   taskUpdated={taskUpdated} setTaskUpdated={setTaskUpdated}
                                   setShowAlert={props.setShowAlert}/>
                        )
                      })
                      :
                      <></>
                    }
                    </tbody>
                  </Table>
                </Card.Body>
                <Card.Footer>
                  <Row className="justify-content-md-center">
                    <Col md="auto">
                      <AdvancedPagination countItems={countItems} updatePage={updatePage}></AdvancedPagination>
                    </Col>
                  </Row>
                </Card.Footer>
              </div>
            </Collapse>
          </Card>
        </Col>
      </Row>

      <Modal size='lg' show={modalCreate} onHide={() => setModalCreate(false)}
             aria-labelledby="contained-modal-title-vcenter" centered>
        <Modal.Body>
          <Row>
            <Col>
              <Card>
                <Card.Header>
                  <Row>
                    <Col>
                      <Card.Title as="h5">{t('ngen.tasks')}</Card.Title>
                      <span className="d-block m-t-5">{t('w.add')} {t('ngen.tasks')}</span>
                    </Col>
                    <Col sm={12} lg={2}>
                      <CloseButton aria-label={t('w.close')} onClick={() => setModalCreate(false)}/>
                    </Col>
                  </Row>
                </Card.Header>
                <Card.Body>
                  <FormCreateTask name={name} setName={setName}
                                  priority={priority} setPriority={setPriority}
                                  description={description} setDescription={setDescription}
                                  playbook={playbook}
                                  ifConfirm={createTask} ifCancel={() => setModalCreate(false)}/>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Modal.Body>
      </Modal>
    </React.Fragment>
  )
}

export default ListTask; 
