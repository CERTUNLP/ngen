import React, { useEffect, useState } from 'react'
import { Card, Col, Row } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import TableUsers from './components/TableUsers'
import Navigation from '../../components/Navigation/Navigation'
import Search from '../../components/Search/Search'
import CrudButton from '../../components/Button/CrudButton'
import { getUsers } from '../../api/services/users'
import AdvancedPagination from '../../components/Pagination/AdvancedPagination'
import Alert from '../../components/Alert/Alert'
import { useTranslation } from 'react-i18next'

function ListUser () {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState()
  const { t } = useTranslation()

  const [currentPage, setCurrentPage] = useState(1)
  const [updatePagination, setUpdatePagination] = useState(false)
  const [disabledPagination, setDisabledPagination] = useState(true)

  const [countItems, setCountItems] = useState(0)

  const [showAlert, setShowAlert] = useState(false)

  const [wordToSearch, setWordToSearch] = useState('')
  const [order, setOrder] = useState('')

  function updatePage (chosenPage) {
    setCurrentPage(chosenPage)
  }

  const resetShowAlert = () => {
    setShowAlert(false)
  }
  useEffect(() => {
    getUsers(currentPage, wordToSearch, order).then((response) => {
      //es escencial mantener este orden ya que si no proboca bugs en el paginado
      setUsers(response.data.results)
      setCountItems(response.data.count)
      if (currentPage === 1) {
        setUpdatePagination(true)
      }
      setDisabledPagination(false)

    }).catch((error) => {
      setError(error)
    }).finally(() => {
      setShowAlert(true)
      setLoading(false)
    })

  }, [currentPage, wordToSearch, order])

  if (error) {
    return <p>{t('user.error.fetch')}</p>
  }

  return (
    <div>
      <Alert showAlert={showAlert} resetShowAlert={resetShowAlert}/>
      <Row>
        <Navigation actualPosition={t('menu.users')}/>
      </Row>
      <Card>
        <Card.Header>
          <Row>
            <Col sm={12} lg={8}>
              <Search type={t('search.by.name.user.email')}
                      setWordToSearch={setWordToSearch}
                      wordToSearch={wordToSearch} setLoading={setLoading}/>
            </Col>
            <Col sm={12} lg={3}>
              <Link to="/users/create">
                <CrudButton type="create" name={t('ngen.user')}/>
              </Link>

            </Col>
          </Row>
          <Row>
          </Row>
        </Card.Header>
        <Card.Body>
          <TableUsers users={users} loading={loading} order={order}
                      setOrder={setOrder} setLoading={setLoading}
                      currentPage={currentPage}/>
        </Card.Body>
        <Card.Footer>
          <Row className="justify-content-md-center">
            <Col md="auto">
              <AdvancedPagination countItems={countItems}
                                  updatePage={updatePage}
                                  updatePagination={updatePagination}
                                  setUpdatePagination={setUpdatePagination}
                                  setLoading={setLoading}
                                  setDisabledPagination={setDisabledPagination}
                                  disabledPagination={disabledPagination}/>
            </Col>
          </Row>
        </Card.Footer>
      </Card>
    </div>

  )
}

export default ListUser
