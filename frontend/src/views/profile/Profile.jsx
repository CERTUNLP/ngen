import React, { useEffect, useState } from "react";
import { Card, Col, Form, Row, Table, Modal, Button } from "react-bootstrap";
import { getProfile, getApiKey } from "../../api/services/profile";
import { getGroup } from "../../api/services/groups";
import { getPermission } from "../../api/services/permissions";
import Navigation from "../../components/Navigation/Navigation";
import FormGetName from "../../components/Form/FormGetName";
import { getPriority } from "../../api/services/priorities";
import ActiveButton from "../../components/Button/ActiveButton";
import { useTranslation } from "react-i18next";

const Profile = () => {
  const [profile, setProfile] = useState([]);
  const [apikey, setApikey] = useState("");
  const [password, setPassword] = useState("");
  const [show, setShow] = useState(false);

  const { t } = useTranslation();

  const handleGetApiKey = () => {
    getApiKey(profile.username, password).then((response) => {
      setApikey(response.data.token);
      setShow(false);
    });
  };

  useEffect(() => {
    getProfile()
      .then((response) => {
        setProfile(response.data[0]);
      })
      .catch((error) => {
        console.log(error);
      });
  }, []);

  return (
    <div>
      <Row>
        <Navigation actualPosition={t("menu.profile")} />
      </Row>
      <Modal show={show} onHide={() => setShow(false)}>
        <Modal.Header closeButton>
          <Modal.Title>{t("ngen.password")}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form.Label>{t("ngen.user.ask_password")}</Form.Label>
          <Form.Control
            type="password"
            placeholder={t("ngen.password")}
            onChange={(e) => setPassword(e.target.value)}
          />
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShow(false)}>
            {t("w.close")}
          </Button>
          <Button variant="primary" onClick={handleGetApiKey}>
            {t("ngen.accept")}
          </Button>
        </Modal.Footer>
      </Modal>
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <Row>
                <Col>
                  <Card.Title as="h5">
                    {t("ngen.user.profile")}: {profile.username}
                  </Card.Title>
                </Col>
              </Row>
            </Card.Header>
            <Card.Body>
              <Table responsive>
                <tbody>
                  {profile.username !== undefined ? (
                    <tr>
                      <td>{t("ngen.user.username")}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={profile.username} />
                      </td>
                    </tr>
                  ) : (
                    <></>
                  )}
                  {profile.email !== undefined ? (
                    <tr>
                      <td>{t("w.email")}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={profile.email} />
                      </td>
                    </tr>
                  ) : (
                    <></>
                  )}
                  {profile.first_name !== undefined ? (
                    <tr>
                      <td>{t("ngen.name_one")}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={profile.first_name} />
                      </td>
                    </tr>
                  ) : (
                    <></>
                  )}
                  {profile.last_name !== undefined ? (
                    <tr>
                      <td>{t("ngen.last.name")}</td>
                      <td>
                        <Form.Control plaintext readOnly defaultValue={profile.last_name} />
                      </td>
                    </tr>
                  ) : (
                    <></>
                  )}
                  {profile.is_active !== undefined ? (
                    <tr>
                      <td>{t("w.active")}</td>
                      <td>
                        <ActiveButton active={profile.is_active} />
                      </td>
                    </tr>
                  ) : (
                    <></>
                  )}
                  {profile.is_superuser !== undefined ? (
                    <tr>
                      <td> {t("ngen.user.is.superuser")}</td>
                      <td>
                        <ActiveButton active={profile.is_superuser} />
                      </td>
                    </tr>
                  ) : (
                    <></>
                  )}
                  {profile.is_staff !== undefined ? (
                    <tr>
                      <td> {t("ngen.user.is.staff")}</td>
                      <td>
                        <ActiveButton active={profile.is_staff} />
                      </td>
                    </tr>
                  ) : (
                    <></>
                  )}
                  {profile.is_network_admin !== undefined ? (
                    <tr>
                      <td> {t("ngen.user.is.network_admin")}</td>
                      <td>
                        <ActiveButton active={profile.is_network_admin} />
                      </td>
                    </tr>
                  ) : (
                    <></>
                  )}
                  <tr>
                    <td>{t("ngen.apikey")}</td>
                    <td>
                      <Form.Control
                        plaintext
                        readOnly
                        value={apikey}
                        hidden={!apikey}
                      />
                      <button className="btn btn-primary" type="button" onClick={() => setShow(true)} hidden={apikey} >
                        {t("w.show")}
                      </button>
                    </td>
                  </tr>
                  {profile.date_joined !== undefined ? (
                    <tr>
                      <td>{t("date.creation")}</td>
                      <td>
                        <Form.Control
                          plaintext
                          readOnly
                          defaultValue={profile.date_joined.slice(0, 10) + " " + profile.date_joined.slice(11, 19)}
                        />
                      </td>
                    </tr>
                  ) : (
                    <></>
                  )}
                  {profile.last_login !== undefined ? (
                    <tr>
                      <td>{t("session.last")}</td>
                      <td>
                        <Form.Control
                          plaintext
                          readOnly
                          defaultValue={profile.last_login.slice(0, 10) + " " + profile.last_login.slice(11, 19)}
                        />
                      </td>
                    </tr>
                  ) : (
                    <></>
                  )}
                  {profile.priority !== undefined ? (
                    <tr>
                      <td>{t("ngen.priority_one")}</td>
                      <td>
                        <FormGetName form={true} get={getPriority} url={profile.priority} key={1} />
                      </td>
                    </tr>
                  ) : (
                    <></>
                  )}

                  {profile.groups !== undefined && profile.groups.length >= 0 ? (
                    <tr>
                      <td>{t("w.groups")}</td>
                      <td>
                        {Object.values(profile.groups).map((groupItem, index) => {
                          return <FormGetName form={true} get={getGroup} url={groupItem} key={index} />;
                        })}
                      </td>
                    </tr>
                  ) : (
                    <></>
                  )}
                  {profile.user_permissions !== undefined && profile.user_permissions.length >= 0 ? (
                    <tr>
                      <td>{t("w.permissions")}</td>
                      <td>
                        {Object.values(profile.user_permissions).map((permissionItem, index) => {
                          return <FormGetName form={true} get={getPermission} url={permissionItem} key={index} />;
                        })}
                      </td>
                    </tr>
                  ) : (
                    <></>
                  )}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Profile;
