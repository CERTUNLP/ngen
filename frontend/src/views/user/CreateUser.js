import React, { useState, useEffect } from 'react';
import { Card, Form } from 'react-bootstrap';
import { postUser } from "../../api/services/users";
import { getMinifiedPriority } from "../../api/services/priorities";
import Alert from '../../components/Alert/Alert';
import FormUser from './components/FormUser'
import Navigation from '../../components/Navigation/Navigation'
import { useTranslation, Trans } from 'react-i18next';


const AddUser = () => {
    const formEmpty = {
        username: "",
        first_name: "",
        last_name: "",
        email: "",
        is_active: true,
        priority: '',
        password: "",
        passwordConfirmation: ""
    }

    const [body, setBody] = useState(formEmpty)
    const [priorities, setPriorities] = useState([])
    const [loading, setLoading] = useState(true)
    const [showAlert, setShowAlert] = useState(false)
    const { t } = useTranslation();

    useEffect(() => {
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

    const createUser = (e) => {

        postUser(body.username, body.first_name, body.last_name, body.email, body.priority, body.is_active, body.password)
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
            <Navigation actualPosition={t('w.add') + t('ngen.user')} path="/users" index={t('ngen.user_other')} />
            <Card>
                <Card.Header>

                    <Card.Title as="h5">{t('w.add')} {t('ngen.user')}</Card.Title>
                </Card.Header>
                <Card.Body>
                    <Form >
                        <FormUser body={body} setBody={setBody} priorities={priorities} createUser={createUser} loading={loading} />
                    </Form>
                </Card.Body>
            </Card>
        </>
    )
}

export default AddUser
