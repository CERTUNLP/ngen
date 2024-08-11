import React, { useEffect, useState } from 'react';
import { Card, Col, Row } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import CrudButton from '../../components/Button/CrudButton';
import Alert from '../../components/Alert/Alert';
import AdvancedPagination from '../../components/Pagination/AdvancedPagination';
import Navigation from '../../components/Navigation/Navigation'
import { getMinifiedTaxonomy, getTaxonomies } from '../../api/services/taxonomies';
import Search from '../../components/Search/Search';
import TableTaxonomy from './components/TableTaxonomy';
import { useTranslation } from 'react-i18next';
import { getMinifiedTaxonomyGroups } from "../../api/services/taxonomyGroups";

const ListTaxonomies = () => {
  const [taxonomies, setTaxonomies] = useState([]);
  const [taxonomyGroups, setTaxonomyGroups] = useState([])
  const [minifiedTaxonomies, setMinifiedTaxonomies] = useState([])
  const [isModify, setIsModify] = useState(null);
  const [loading, setLoading] = useState(true)
  const { t } = useTranslation();

  const [showAlert, setShowAlert] = useState(false);

  const [currentPage, setCurrentPage] = useState(1)
  const [countItems, setCountItems] = useState(0);
  const [updatePagination, setUpdatePagination] = useState(false)
  const [disabledPagination, setDisabledPagination] = useState(true)
  const [wordToSearch, setWordToSearch] = useState('')

  const [order, setOrder] = useState("name");


  function updatePage(chosenPage) {
    setCurrentPage(chosenPage);
  }

  useEffect(() => {
    getTaxonomies(currentPage, wordToSearch, order).then((response) => {
      setCountItems(response.data.count)
      setTaxonomies(response.data.results)
      if (currentPage === 1) {
        setUpdatePagination(true)
      }
      setDisabledPagination(false)
    }).catch((error) => {
      //alert
      console.log(error)
    }).finally(() => {
      setShowAlert(true)
      setLoading(false)
    })

    const fetchTaxonomyGroups = async () => {
      setLoading(true)
      getMinifiedTaxonomyGroups().then((response) => {
        let dicTaxonomyGroups = {}
        response.map((tg) => {
          dicTaxonomyGroups[tg.url] = tg.name
          return null
        })
        setTaxonomyGroups(dicTaxonomyGroups)
      }).catch((error) => {
        console.log(error)
      }).finally(() => {
        setLoading(false)
      })
    }
    fetchTaxonomyGroups()

    const fetchMinifiedTaxonomies = async () => {
      setLoading(true)
      getMinifiedTaxonomy().then((response) => {
        let dicMinifiedTaxonomy = {}
        response.map((tg) => {
          dicMinifiedTaxonomy[tg.url] = tg.name
          return null
        })
        setMinifiedTaxonomies(dicMinifiedTaxonomy)
      }).catch((error) => {
        console.log(error)
      }).finally(() => {
        setLoading(false)
      })
    }
    fetchMinifiedTaxonomies()

  }, [currentPage, isModify, order, wordToSearch,]);


  return (
    <React.Fragment>
      <Alert showAlert={showAlert} resetShowAlert={() => setShowAlert(false)} component="taxonomy"/>

      <Row>
        <Navigation actualPosition={t('ngen.taxonomy_other')}/>
      </Row>
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <Row>
                <Col sm={12} lg={9}>
                  <Search type={t('search.by.name')} setWordToSearch={setWordToSearch} wordToSearch={wordToSearch}
                          setLoading={setLoading}/>
                </Col>

                <Col sm={12} lg={3}>
                  <Link to={{ pathname: './taxonomies/create' }}>
                    <CrudButton type='create' name={t('ngen.taxonomy_one')}/>
                  </Link>
                </Col>
              </Row>
            </Card.Header>
            <Card.Body>
              <TableTaxonomy setIsModify={setIsModify} list={taxonomies} loading={loading} order={order}
                             setOrder={setOrder} setLoading={setLoading} taxonomyGroups={taxonomyGroups}
                             minifiedTaxonomies={minifiedTaxonomies}/>
            </Card.Body>
            <Card.Footer>
              <Row className="justify-content-md-center">
                <Col md="auto">
                  <AdvancedPagination countItems={countItems} updatePage={updatePage}
                                      updatePagination={updatePagination} setUpdatePagination={setUpdatePagination}
                                      setLoading={setLoading} setDisabledPagination={setDisabledPagination}
                                      disabledPagination={disabledPagination}/>
                </Col>
              </Row>
            </Card.Footer>
          </Card>
        </Col>
      </Row>
    </React.Fragment>
  );
};

export default ListTaxonomies;
