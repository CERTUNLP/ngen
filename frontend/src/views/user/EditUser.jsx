import React, { useEffect, useState } from 'react'
import { Card } from 'react-bootstrap'
import { getUser, putUser } from '../../api/services/users'
import { useLocation, useParams } from 'react-router-dom';
import Alert from '../../components/Alert/Alert'
import { getMinifiedPriority } from '../../api/services/priorities'
import FormUser from './components/FormUser'
import Navigation from '../../components/Navigation/Navigation'
import { useTranslation } from 'react-i18next'
import { COMPONENT_URL } from 'config/constant';

const EditUser = () => {
  const location = useLocation()
  const fromState = location.state
  const [user, setUser] = useState({});
  // const [body, setBody] = useState({})
  const [loading, setLoading] = useState(true)
  const [priorities, setPriorities] = useState([])
  const [showAlert, setShowAlert] = useState(false)
  const [id, setId] = useState(useParams());
  const { t } = useTranslation()

  useEffect(() => {
    getMinifiedPriority().then((response) => {
      let listPriority = []
      response.map((priority) => {
        listPriority.push({ value: priority.url, label: priority.name })
      })
      setPriorities(listPriority)
    }).catch((error) => {
      console.log(error)

    })
  }, []);

  useEffect(() => {

    if (id) {
      getUser(COMPONENT_URL.user + id.id + "/").then((response) => {
        setUser(response.data)
      }).catch((error) => {
        console.log(error)

      }).finally(() => {
        setLoading(false)
      })
    }

  }, [id]);

  const resetShowAlert = () => {
    setShowAlert(false)
  }

  const editUser = (e) => {

    putUser(user.url, user.username, user.first_name, user.last_name,
      user.email, user.priority).then(() => {
        window.location.href = '/users'
      }).catch((error) => {
        setShowAlert(true)
        console.log(error)
      })

  }
  return (
    <>
      <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} />
      <Navigation actualPosition={t('w.edit') + t('ngen.user')} path="/users"
        index={t('ngen.user_other')} />
      <Card>
        <Card.Header>
          <Card.Title as="h5">{t('w.edit')} {t('ngen.user')}</Card.Title>
        </Card.Header>
        <Card.Body>
          <FormUser body={user} setBody={setUser} priorities={priorities}
            createUser={editUser} loading={loading}
            passwordRequired={false} />
        </Card.Body>
      </Card>
    </>
  )
}

export default EditUser
