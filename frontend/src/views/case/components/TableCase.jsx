import React, { useEffect, useState } from 'react';
import { Button, Form, Row, Spinner, Table } from 'react-bootstrap';
import CrudButton from '../../../components/Button/CrudButton';
import { deleteCase } from '../../../api/services/cases';
import { Link } from 'react-router-dom';
import ModalConfirm from '../../../components/Modal/ModalConfirm';
import Ordering from '../../../components/Ordering/Ordering';
import LetterFormat from '../../../components/LetterFormat';
import ListDomain from './ListDomain';
import { useTranslation } from 'react-i18next';

const TableCase = ({
  setIfModify,
  cases,
  loading,
  setLoading,
  selectedCases,
  setSelectedCases,
  setOrder,
  order,
  priorityNames,
  stateNames,
  tlpNames,
  userNames,
  editColum,
  deleteColum,
  detailModal,
  modalCaseDetail,
  navigationRow,
  selectCase,
  handleClickRadio,
  setSelectCase,
  disableCheckbox,
  disableDate,
  disableName,
  disablePriority,
  disableTlp,
  disableNubersOfEvents,
  deleteColumForm,
  deleteCaseFromForm,
  disableColumOption,
  disableUuid,
  disableDateModified
}) => {
  const [url, setUrl] = useState(null);
  const [modalDelete, setModalDelete] = useState(false);
  const [id, setId] = useState(null);

  //checkbox
  const [isCheckAll, setIsCheckAll] = useState(false);

  const [list, setList] = useState([]);

  const { t } = useTranslation();

  //ORDER
  useEffect(() => {
    setList(cases);
  }, [cases]);

  const storageCaseUrl = (url) => {
    localStorage.removeItem('case');
    localStorage.removeItem('navigation');
    localStorage.removeItem('button return');
    localStorage.setItem('case', url);
    localStorage.setItem('navigation', navigationRow);
    localStorage.setItem('button return', navigationRow);
    window.location.href = '/cases/edit';
  };

  const handleOnClick = (url) => {
    localStorage.setItem('case', url);
    localStorage.setItem('navigation', navigationRow);
    localStorage.setItem('button return', navigationRow);
  };

  if (loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
      </Row>
    );
  }

  //Remove Case
  const Delete = (url, id) => {
    setId(id);
    setUrl(url);
    setModalDelete(true);
  };

  const removeCase = (url) => {
    deleteCase(url)
      .then((response) => {
        setIfModify(response);
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        setModalDelete(false);
      });
  };

  //Checkbox
  const handleSelectAll = () => {
    setIsCheckAll(!isCheckAll);
    setSelectedCases(list.filter((item) => !item.blocked).map((li) => li.url));
    if (isCheckAll) {
      setSelectedCases([]);
    }
  };
  const handleClick = (e) => {
    const { id, checked } = e.target;
    setSelectedCases([...selectedCases, id]);
    if (!checked) {
      setSelectedCases(selectedCases.filter((item) => item !== id));
    }
  };

  const letterSize = { fontSize: '1.0em' };
  return (
    <React.Fragment>
      <Table responsive hover className="text-center">
        <thead>
          <tr>
            {!disableCheckbox &&
              (selectCase ? (
                <th></th>
              ) : list.length > 0 ? (
                <th>
                  <Form.Group>
                    <Form.Check
                      type="checkbox"
                      id={'selectAll'}
                      onChange={handleSelectAll}
                      checked={selectedCases.length !== 0 ? selectedCases.length === list.length : false}
                    />
                  </Form.Group>
                </th>
              ) : (
                <th>
                  <Form.Group>
                    <Form.Check custom type="checkbox" disabled />
                  </Form.Group>
                </th>
              ))}
            {!disableDate && (
              <Ordering
                field="created"
                label={t('creation.date')}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                letterSize={letterSize}
              />
            )}
            {!disableDateModified && (
              <Ordering
                field="modified"
                label={t('ngen.date.modified')}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                letterSize={letterSize}
              />
            )}
            {!disableUuid && <th style={letterSize}> {t('ngen.uuid')} </th>}
            {!disableName && <th style={letterSize}> {t('ngen.name_one')} </th>}
            {!disablePriority && (
              <Ordering
                field="priority"
                label={t('ngen.priority_one')}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
                letterSize={letterSize}
              />
            )}
            {!disableTlp && <th style={letterSize}> {t('ngen.tlp')} </th>}
            <th style={letterSize}> {t('ngen.state_one')} </th>
            <th style={letterSize}> {t('ngen.event_other')} </th>
            {!disableNubersOfEvents && <th style={letterSize}> {t('ngen.event.quantity')} </th>}
            <th style={letterSize}> {t('ngen.status.assigned')} </th>
            {!disableColumOption && <th style={letterSize}> {t('ngen.action_one')} </th>}
          </tr>
        </thead>
        <tbody>
          {list.map((caseItem, index) => {
            return (
              <tr key={index}>
                {!disableCheckbox && (
                  <td>
                    {selectCase ? (
                      <Form.Group>
                        <Form.Check
                          type="checkbox"
                          id={caseItem.url} //Fecha de inicio de gestiónunfold_more	Nombre	Prioridadunfold_more	TLP	Estado	Asignado
                          onChange={(event) =>
                            handleClickRadio(
                              event,
                              caseItem.url,
                              caseItem.name,
                              caseItem.date,
                              priorityNames[caseItem.priority],
                              tlpNames[caseItem.tlp].name,
                              stateNames[caseItem.state],
                              userNames[caseItem.user_creator]
                            )
                          }
                          checked={selectedCases.includes(caseItem.url)}
                        />
                      </Form.Group>
                    ) : (
                      <Form.Group>
                        <Form.Check
                          disabled={caseItem.blocked}
                          type="checkbox"
                          id={caseItem.url}
                          onChange={handleClick}
                          checked={selectedCases.includes(caseItem.url)}
                        />
                      </Form.Group>
                    )}
                  </td>
                )}
                {!disableDate && <td>{caseItem ? caseItem.date.slice(0, 10) + ' ' + caseItem.date.slice(11, 19) : ''}</td>}

                {!disableDateModified && <td>{caseItem ? caseItem.modified.slice(0, 10) + ' ' + caseItem.modified.slice(11, 19) : ''}</td>}

                {!disableUuid && <td>{caseItem.uuid}</td>}

                {!disableName && <td>{caseItem.name || '-'}</td>}

                {!disablePriority && <td>{priorityNames[caseItem.priority]}</td>}
                {!disableTlp && (
                  <td>
                    <LetterFormat useBadge={true} stringToDisplay={tlpNames[caseItem.tlp].name} color={tlpNames[caseItem.tlp].color} />
                  </td>
                )}
                <td>{stateNames[caseItem.state] || '-'}</td>
                <td>
                  <ListDomain events={caseItem.events} />
                </td>
                {!disableNubersOfEvents && <td>{caseItem.events_count}</td>}
                <td>{userNames[caseItem.assigned] || '-'}</td>
                <td>
                  {!disableColumOption && detailModal ? (
                    <CrudButton
                      type="read"
                      onClick={() =>
                        modalCaseDetail(
                          caseItem.url,
                          caseItem.name,
                          caseItem.name,
                          caseItem.date,
                          priorityNames[caseItem.priority],
                          tlpNames[caseItem.tlp].name,
                          stateNames[caseItem.state],
                          userNames[caseItem.user_creator]
                        )
                      }
                    />
                  ) : (
                    <Link to="/cases/view">
                      <CrudButton type="read" onClick={() => storageCaseUrl(caseItem.url)} />
                    </Link>
                  )}
                  {!disableColumOption &&
                    editColum &&
                    (!caseItem.blocked ? (
                      <Link to="/cases/edit" state={caseItem.url}>
                        <CrudButton type="edit" />
                      </Link>
                    ) : (
                      <Button
                        id="button_hover"
                        className="btn-icon btn-rounded"
                        variant="outline-warning"
                        title={t('ngen.case_one') + t('w.solved')}
                        disabled
                        style={{
                          border: '1px solid #555',
                          borderRadius: '50px',
                          color: '#555'
                        }}
                      >
                        <i className="fa fa-edit" style={{ color: '#555' }}></i>
                      </Button>
                    ))}
                  {!disableColumOption &&
                    deleteColum &&
                    (deleteColumForm ? (
                      <CrudButton type="delete" onClick={() => deleteCaseFromForm(caseItem.url)} />
                    ) : (
                      <CrudButton type="delete" onClick={() => Delete(caseItem.url)} />
                    ))}
                </td>
              </tr>
            );
          })}
        </tbody>
      </Table>
      <ModalConfirm
        type="delete"
        component="Caso"
        name={`${t('ngen.case_one')}${id}`}
        showModal={modalDelete}
        onHide={() => setModalDelete(false)}
        ifConfirm={() => removeCase(url)}
      />
    </React.Fragment>
  );
};

export default TableCase;
