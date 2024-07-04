import React, { useState, useEffect } from 'react';
import { Card, Form } from 'react-bootstrap';
import { putUser, getUser } from "../../api/services/users";
import { useLocation } from "react-router-dom";
import Alert from '../../components/Alert/Alert';
import { getMinifiedPriority } from "../../api/services/priorities";
import FormUser from './components/FormUser'
import Navigation from '../../components/Navigation/Navigation'
import { useTranslation, Trans } from 'react-i18next';


const EditUser = () => {
    const location = useLocation();
    const fromState = location.state;
    const [user, setUser] = useState(fromState);
    const [body, setBody] = useState({})
    const [loading, setLoading] = useState(true)
    const [priorities, setPriorities] = useState([])
    const [showAlert, setShowAlert] = useState(false)
    const { t } = useTranslation();

    useEffect(() => {

        getUser(user.url).then((response) => {
            setUser(response.data)
            console.log(response.data)
        })

        const fetchPosts = async () => {
            setLoading(true)
            getMinifiedPriority().then((response) => {
                let listPriority = []
                response.map((priority) => {
                    listPriority.push({ value: priority.url, label: priority.name })
                })
                setPriorities(listPriority)
            })
                .catch((error) => {
                    console.log(error)

                }).finally(() => {
                    setLoading(false)
                })

        }

        fetchPosts()


    }, []);
    const resetShowAlert = () => {
        setShowAlert(false);
    }

    const editUser = (e) => {

        putUser(body.url, body.username, body.first_name, body.last_name, body.email, body.priority)
            .then(() => {
                window.location.href = '/users';
            })
            .catch((error) => {
                setShowAlert(true)
                console.log(error)
            })

    }
    return (
        <>
            <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} />
            <Navigation actualPosition={t('w.edit') + t('ngen.user')} path="/users" index={t('ngen.user_other')} />
            <Card>

                <Card.Header>
                    <Card.Title as="h5">{t('w.edit')} {t('ngen.user')}</Card.Title>
                </Card.Header>
                <Card.Body>
                    <Form>
                        <FormUser body={user} setBody={setUser} priorities={priorities} createUser={editUser} loading={loading} />

                    </Form>
                </Card.Body>
            </Card>
        </>
    )
}
export default EditUser
