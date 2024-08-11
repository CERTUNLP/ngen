import React, { useEffect } from 'react';
import { Form } from 'react-bootstrap';
import {
  validateContactMail,
  validateContactPhone,
  validateContactTelegram,
  validateContactURI
} from '../../../utils/validators/contact';
import { useTranslation } from 'react-i18next';

const FormContactSelectUsername = (props) => {
  // props: selectedType, contact, setContact, setValidContact
  useEffect(() => {
    if (username) {
      props.setValidContact(!props.contact || username.condition)
    }
  }, [props.contact, props.selectedType]);
  const { t } = useTranslation();
  const typeValue = [
    {
      name: 'email',
      placeholder: t('ngen.email_add'),
      isInvalid: JSON.parse(!validateContactMail(props.contact)),
      condition: JSON.parse(validateContactMail(props.contact)),
      messageDanger: t('ngen.email_valid')

    },
    {
      name: 'telegram',
      placeholder: t('ngen.telegram_add'),
      isInvalid: JSON.parse(!validateContactTelegram(props.contact)),
      condition: JSON.parse(validateContactTelegram(props.contact)),
      messageDanger: t('ngen.telegram_valid')
    },
    {
      name: 'phone',
      placeholder: t('ngen.phone_add'),
      isInvalid: JSON.parse(!validateContactPhone(props.contact)),
      condition: JSON.parse(validateContactPhone(props.contact)),
      messageDanger: t('ngen.phone_valid')
    },
    {
      name: 'uri',
      placeholder: t('ngen.URI_add'),
      isInvalid: JSON.parse(!validateContactURI(props.contact)),
      condition: JSON.parse(validateContactURI(props.contact)),
      messageDanger: t('ngen.URI_valid')
    }
  ]

  const username = typeValue.find(contact => contact.name === props.selectedType)


  if (username) {
    return (
      <React.Fragment>

        <Form.Group controlId="Form.Contact.Username">
          <Form.Label>{t('ngen.contact_one')}<b style={{ color: "red" }}>*</b></Form.Label>
          <Form.Control
            name="Form.Contact.Username__username"
            placeholder={username.placeholder}
            value={props.contact}
            maxLength="255"
            onChange={(e) => {
              props.setContact(e.target.value)
            }}
            isInvalid={username.isInvalid}
          />
          {!props.contact || username.condition ? "" :
            <div className="invalid-feedback"> {username.messageDanger} </div>}
        </Form.Group>

      </React.Fragment>
    );
  } else {
    return (
      <React.Fragment>
        <Form.Group controlId="Form.Contact.Username.readOnly">
          <Form.Label>{t('ngen.contact_one')} <b style={{ color: "red" }}>*</b></Form.Label>
          <Form.Control readOnly
                        placeholder={t('placeholder.contact')}
                        name="username"/>
        </Form.Group>
      </React.Fragment>
    );
  }
};

export default FormContactSelectUsername;
