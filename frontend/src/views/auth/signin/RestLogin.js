import React, { useState, useEffect } from 'react';
import { Row, Col, Button } from 'react-bootstrap';
import { useHistory, useLocation } from 'react-router-dom';


import * as Yup from 'yup';
import { Formik } from 'formik';
import useScriptRef from '../../../hooks/useScriptRef';

import { LOGIN } from './../../../store/actions';
import { login } from '../../../api/services/auth';
import { store } from './../../../store';
import Alert from './../../../components/Alert/Alert';
import { useTranslation, Trans } from 'react-i18next';


const RestLogin = ({ className, ...rest }) => {
    const [showAlert, setShowAlert] = useState(false);

    const { dispatch } = store;

    const resetShowAlert = () => {
        setShowAlert(false);
    }
    const { t } = useTranslation();

    const validationMessages = {
        un: t('validation.username'),
        pw: t('validation.password')
    };


    return (
        <React.Fragment>
            <Alert showAlert={showAlert} resetShowAlert={resetShowAlert} />
            <Formik
                initialValues={{
                    username: '',
                    password: '',
                    submit: null
                }}
                validationSchema={Yup.object().shape({
                    username: Yup.string().max(255).required(validationMessages.un),
                    password: Yup.string().max(255).required(validationMessages.pw)
                })}
                onSubmit={async (values, { setErrors, setStatus, setSubmitting }) => {

                    login(values.username, values.password)
                        .then((response) => {
                            dispatch({
                                type: LOGIN,
                                payload: { user: response.data.user, token: response.data.access }
                            });
                        })
                        .catch((error) => {
                            setShowAlert(true);
                        });
                }}
            >
                {
                    ({ errors, handleBlur, handleChange, handleSubmit, isSubmitting, touched, values }) => (
                        <form noValidate onSubmit={handleSubmit} className={className} {...rest}>
                            <div className="form-group mb-3">
                                <input
                                    className="form-control"
                                    error={touched.username && errors.username}
                                    label="Username"
                                    placeholder={t('ngen.user.username')}
                                    name="username"
                                    onBlur={handleBlur}
                                    onChange={handleChange}
                                    type="text"
                                    value={values.username}
                                />
                                {touched.username && errors.username && <small className="text-danger form-text">{errors.username}</small>}
                            </div>
                            <div className="form-group mb-4">
                                <input
                                    className="form-control"
                                    error={touched.password && errors.password}
                                    label="Password"
                                    placeholder={t('ngen.password')}
                                    name="password"
                                    onBlur={handleBlur}
                                    onChange={handleChange}
                                    type="password"
                                    value={values.password}
                                />
                                {touched.password && errors.password && <small className="text-danger form-text">{errors.password}</small>}
                            </div>

                            <Row>
                                <Col mt={2}>
                                    <Button
                                        className="btn-block"
                                        color="primary"
                                        disabled={isSubmitting}
                                        size="large"
                                        type="submit"
                                        variant="primary"
                                    >
                                        {t('button.login')}
                                    </Button>
                                </Col>
                            </Row>
                        </form>
                    )}
            </Formik>
            <hr />



        </React.Fragment>
    );
};

export default RestLogin;
