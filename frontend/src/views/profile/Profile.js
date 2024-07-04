import React, { useState, useEffect } from 'react'
import { Card, Table, Row, Col, Form } from 'react-bootstrap';
import { getProfile } from "../../api/services/profile";
import { getGroup } from "../../api/services/groups";
import { getPermission } from "../../api/services/permissions";
import Navigation from '../../components/Navigation/Navigation'
import FormGetName from '../../components/Form/FormGetName';
import { getPriority } from '../../api/services/priorities';
import ActiveButton from '../../components/Button/ActiveButton';
import { useTranslation, Trans } from 'react-i18next';

const Profile = () => {

    const [profile, setProfile] = useState([])
    const { t } = useTranslation();
    useEffect(() => {

        getProfile().then((response) => {
            setProfile(response.data[0])
            console.log(response.data[0])

        })
            .catch((error) => {

            })


    }, [])
    console.log(profile)

    /* 
      {
          "id": 1,
          "username": "ngen",
          "email": "ngen@ngen.com",
          "first_name": "ngen",
          "last_name": "ngen",
          "is_active": true,
          "is_staff": true,
          "is_superuser": true,
          "date_joined": "2022-04-02T22:52:32.851000Z",
          "last_login": "2024-02-19T02:23:48.445540Z",
          "priority": "http://localhost:8000/api/administration/priority/5/",
          "groups": [],
          "user_permissions": []
      }
    */

    return (
        <div>
            <Row>
                <Navigation actualPosition="" />
            </Row>
            <Row>
                <Col>
                    <Card>
                        <Card.Header>
                            <Row>
                                <Col>
                                    <Card.Title as="h5">{t('ngen.user.profile')}: {profile.username}</Card.Title>
                                </Col>
                            </Row>
                        </Card.Header>
                        <Card.Body>
                            <Table responsive >
                                <tbody>
                                    {profile.first_name ?
                                        <tr>
                                            <td>{t('ngen.name_one')}</td>
                                            <td>
                                                <Form.Control plaintext readOnly defaultValue={profile.first_name} />
                                            </td>
                                        </tr>
                                        :
                                        <></>
                                    }
                                    {profile.last_name ?
                                        <tr>
                                            <td>{t('ngen.last.name')}</td>
                                            <td>
                                                <Form.Control plaintext readOnly defaultValue={profile.last_name} />
                                            </td>
                                        </tr>
                                        :
                                        <></>
                                    }
                                    {profile.is_active ?
                                        <tr>
                                            <td>{t('w.active')}</td>
                                            <td>
                                                <ActiveButton active={profile.is_active} />
                                            </td>
                                        </tr>
                                        :
                                        <></>
                                    }
                                    {profile.is_superuser ?
                                        <tr>
                                            <td> {t('ngen.user.is.superuser')}</td>
                                            <td>
                                                <ActiveButton active={profile.is_superuser} />
                                            </td>
                                        </tr>
                                        :
                                        <></>
                                    }
                                    {profile.is_staff ?
                                        <tr>
                                            <td> {t('ngen.user.is.staff')}</td>
                                            <td>
                                                <ActiveButton active={profile.is_staff} />
                                            </td>
                                        </tr>
                                        :
                                        <></>
                                    }
                                    {profile.last_name ?
                                        <tr>
                                            <td>{t('w.active')}</td>
                                            <td>

                                            </td>
                                        </tr>
                                        :
                                        <></>
                                    }

                                    {profile.email ?
                                        <tr>
                                            <td>{t('w.email')}</td>
                                            <td>
                                                <Form.Control plaintext readOnly defaultValue={profile.email} />
                                            </td>
                                        </tr>
                                        :
                                        <></>
                                    }
                                    {profile.date_joined ?
                                        <tr>
                                            <td>{t('date.creation')}</td>
                                            <td>
                                                <Form.Control plaintext readOnly defaultValue={profile.date_joined.slice(0, 10) + " " + profile.date_joined.slice(11, 19)} />
                                            </td>
                                        </tr>
                                        :
                                        <></>
                                    }
                                    {profile.last_login ?
                                        <tr>
                                            <td>{t('session.last')}</td>
                                            <td>
                                                <Form.Control plaintext readOnly defaultValue={profile.last_login.slice(0, 10) + " " + profile.last_login.slice(11, 19)} />
                                            </td>
                                        </tr>
                                        :
                                        <></>
                                    }
                                    {profile.priority ?
                                        <tr>
                                            <td>{t('ngen.priority_one')}</td>
                                            <td>
                                                <FormGetName form={true} get={getPriority} url={profile.priority} key={1} />
                                            </td>
                                        </tr>
                                        :
                                        <></>
                                    }

                                    {profile.groups && profile.groups.length > 0 ?
                                        <tr>
                                            <td>{t('w.groups')}</td>
                                            <td>
                                                {Object.values(profile.groups).map((groupItem, index) => {
                                                    return (
                                                        <FormGetName form={true} get={getGroup} url={groupItem} key={index} />
                                                    )
                                                })
                                                }
                                            </td>
                                        </tr>
                                        :
                                        <></>
                                    }
                                    {profile.user_permissions && profile.user_permissions.length > 0 ?
                                        <tr>
                                            <td>{t('w.permissions')}</td>
                                            <td>
                                                {Object.values(profile.user_permissions).map((permissionItem, index) => {
                                                    return (
                                                        <FormGetName form={true} get={getPermission} url={permissionItem} key={index} />
                                                    )
                                                })
                                                }
                                            </td>
                                        </tr>
                                        :
                                        <></>
                                    }

                                </tbody>
                            </Table>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>


        </div>
    )
}

export default Profile