import React, { useEffect, useState } from 'react';
import { Card, Col, Row } from 'react-bootstrap';
import TableContact from './components/TableContact';
import CrudButton from '../../components/Button/CrudButton';
import { getContacts } from '../../api/services/contacts';
import { Link } from 'react-router-dom';
import Navigation from '../../components/Navigation/Navigation';
import Search from '../../components/Search/Search';
import AdvancedPagination from '../../components/Pagination/AdvancedPagination';
import Alert from '../../components/Alert/Alert';
import { useTranslation } from 'react-i18next';

const ListContact = () => {
  const { t } = useTranslation();
  const [contacts, setContacts] = useState([]);
  const [isModify, setIsModify] = useState(null);

  const [loading, setLoading] = useState(true);

  //Alert
  const [showAlert, setShowAlert] = useState(false);

  //AdvancedPagination
  const [currentPage, setCurrentPage] = useState(1);
  const [countItems, setCountItems] = useState(0);
  const [updatePagination, setUpdatePagination] = useState(false);
  const [disabledPagination, setDisabledPagination] = useState(true);

  const [wordToSearch, setWordToSearch] = useState('');

  const [order, setOrder] = useState('name');

  function updatePage(chosenPage) {
    setCurrentPage(chosenPage);
  }

  useEffect(() => {
    setCurrentPage(currentPage); //?

    getContacts(currentPage, wordToSearch, order)
      .then((response) => {
        setContacts(response.data.results);
        //Pagination
        setCountItems(response.data.count);
        if (currentPage === 1) {
          setUpdatePagination(true);
        }
        setDisabledPagination(false);
      })
      .catch((error) => {
        // Show alert
      })
      .finally(() => {
        setShowAlert(true);
        setLoading(false);
      });
  }, [currentPage, isModify, wordToSearch, order]);

  // ------- SEARCH --------
  //filtro
  // let show = []
  // if (!search) {
  //   show = contacts
  // } else {
  //   show = contacts.filter((item) =>
  //     item.name.toLowerCase().includes(search.toLocaleLowerCase())
  //   )
  // }

  return (
    <React.Fragment>
      <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="contact" />
      <Row>
        <Navigation actualPosition={t('ngen.contact_other')} />
      </Row>
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <Row>
                <Col>
                  <Search
                    type={t('w.entityByName')}
                    setWordToSearch={setWordToSearch}
                    wordToSearch={wordToSearch}
                    setLoading={setLoading}
                  />
                </Col>
                <Col sm={3} lg={3}>
                  <Link to="/contacts/create">
                    <CrudButton type="create" name={t('ngen.contact_one')} />
                  </Link>
                </Col>
              </Row>
            </Card.Header>
            <Card.Body>
              <TableContact
                setIsModify={setIsModify}
                list={contacts}
                loading={loading}
                currentPage={currentPage}
                order={order}
                setOrder={setOrder}
                setLoading={setLoading}
              />
            </Card.Body>
            <Card.Footer>
              <Row className="justify-content-md-center">
                <Col md="auto">
                  <AdvancedPagination
                    countItems={countItems}
                    updatePage={updatePage}
                    updatePagination={updatePagination}
                    setUpdatePagination={setUpdatePagination}
                    setLoading={setLoading}
                    setDisabledPagination={setDisabledPagination}
                    disabledPagination={disabledPagination}
                  />
                </Col>
              </Row>
            </Card.Footer>
          </Card>
        </Col>
      </Row>
    </React.Fragment>
  );
};
export default ListContact;
