import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, Col, Row } from 'react-bootstrap';
import Alert from '../../components/Alert/Alert';
import Navigation from '../../components/Navigation/Navigation';
import Search from '../../components/Search/Search';
import CrudButton from '../../components/Button/CrudButton';
import { getPriorities } from '../../api/services/priorities';
import TablePriorities from './components/TablePriorities';
import AdvancedPagination from '../../components/Pagination/AdvancedPagination';
import { useTranslation } from 'react-i18next';

const ListPriorities = () => {
  const [priorities, setPriorities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [countItems, setCountItems] = useState(0);
  const [showAlert, setShowAlert] = useState(false);
  const [wordToSearch, setWordToSearch] = useState('');
  const [updatePagination, setUpdatePagination] = useState(false);
  const [disabledPagination, setDisabledPagination] = useState(true);
  const { t } = useTranslation();

  const [order, setOrder] = useState('name');

  function updatePage(chosenPage) {
    setCurrentPage(chosenPage);
  }

  useEffect(() => {
    getPriorities(currentPage, wordToSearch, order)
      .then((response) => {
        //es escencial mantener este orden ya que si no proboca bugs en el paginado
        setPriorities(response.data.results);
        setCountItems(response.data.count);
        if (currentPage === 1) {
          setUpdatePagination(true);
        }
        setDisabledPagination(false);
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        setShowAlert(true);
        setLoading(false);
      });
  }, [currentPage, wordToSearch, order]);

  const resetShowAlert = () => {
    setShowAlert(false);
  };

  return (
    <div>
      <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} component="priority" />
      <Row>
        <Navigation actualPosition={t('ngen.priority_other')} />
      </Row>

      <Card>
        <Card.Header>
          <Row>
            <Col sm={12} lg={9}>
              <Search type={t('search.by.name')} setWordToSearch={setWordToSearch} wordToSearch={wordToSearch} setLoading={setLoading} />
            </Col>
            <Col sm={12} lg={3}>
              <Link to="/priorities/create">
                <CrudButton type="create" name={t('ngen.priority_one')} />
              </Link>
            </Col>
          </Row>
        </Card.Header>
        <Card.Body>
          <TablePriorities
            Priorities={priorities}
            loading={loading}
            order={order}
            setOrder={setOrder}
            setLoading={setLoading}
            currentPage={currentPage}
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
    </div>
  );
};

export default ListPriorities;
