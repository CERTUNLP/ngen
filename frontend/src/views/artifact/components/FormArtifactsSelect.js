import React, { useEffect } from 'react';
import { Form } from 'react-bootstrap';
import {
    validateSpace, validateEmail, validateURL, validateIP, validateAutonomousSystem,
    validateUserAgent, validateFQDN, validateDomain, validateHexadecimal32,
    validateHexadecimal40, validateHexadecimal64, validateHexadecimal128
} from '../../../utils/validators';
import { useTranslation, Trans } from 'react-i18next';

const FormArtifactsSelect = (props) => {
    // props: selectedType,.value, setContact, setValidContact
    useEffect(() => {
        if (username) {
            props.setValidArtifact(!props.contact || username.condition);
        }
    }, [props.value, props.type]);


    const { t } = useTranslation();
    const typeValue = [
        {
            name: 'mail',
            placeholder: t('ngen.email_add'),
            isInvalid: JSON.parse(!validateSpace(props.value) || !validateEmail(props.value)),
            condition: JSON.parse(validateEmail(props.value)),
            messageDanger: t("ngen.email_valid")

        },
        {
            name: 'domain',
            placeholder: t("ngen.domain_add"),
            isInvalid: JSON.parse(!validateSpace(props.value) || !validateDomain(props.value)),
            condition: "",
            messageDanger: t("ngen.domain_valid")
        },
        {
            name: 'url',
            placeholder: t("ngen.url_add"),
            isInvalid: JSON.parse(!validateSpace(props.value)),
            condition: "",
            messageDanger: t("ngen.url_valid")
        },
        {
            name: 'ip',
            placeholder: t("ngen.ip_add"),
            isInvalid: JSON.parse(!validateSpace(props.value) || !validateIP(props.value)),
            condition: JSON.parse(validateIP(props.value)),
            messageDanger: t("ngen.ip_valid")
        },
        {
            name: 'autonomous-system',
            placeholder: t("ngen.auSys_add"),
            isInvalid: JSON.parse(!validateSpace(props.value) || !validateAutonomousSystem(props.value)),
            condition: JSON.parse(validateAutonomousSystem(props.value)),
            messageDanger: t("ngen.auSys_valid"),
        },
        {
            name: 'user-agent',
            placeholder: t("ngen.userAgent_add"),
            isInvalid: JSON.parse(!validateSpace(props.value) || !validateUserAgent(props.value)),
            condition: JSON.parse(validateUserAgent(props.value)),
            messageDanger: t("ngen.userAgent_valid"),
        },
        {
            name: 'fqdn',
            placeholder: t("ngen.fqdn_add"),
            isInvalid: JSON.parse(!validateSpace(props.value) || !validateDomain(props.value)),
            condition: JSON.parse(validateDomain(props.value)),
            messageDanger: t("ngen.fqdn_valid"),
        },
        {
            name: 'other',
            placeholder: t("ngen.other_add"),
            isInvalid: JSON.parse(!validateSpace(props.value)),
            condition: "",
            messageDanger: t("ngen.URI_valid"),
        },
        {
            name: 'hash',
            placeholder: t("ngen.hex32_add"),
            isInvalid: JSON.parse(!validateSpace(props.value) || (!validateHexadecimal32(props.value) && !validateHexadecimal40(props.value)
                && !validateHexadecimal64(props.value) && !validateHexadecimal128(props.value))),
            condition: JSON.parse(validateHexadecimal32(props.value) || validateHexadecimal40(props.value)
                || validateHexadecimal64(props.value) || validateHexadecimal128(props.value)),
            messageDanger: t("ngen.hex32_valid"),
        }
    ];

    const username = typeValue.find(t => t.name === props.type);


    if (username) {
        return (
            <React.Fragment>

                <Form.Group controlId="formGridAddress1">
                    <Form.Label>{t('ngen.value')}</Form.Label>
                    <Form.Control

                        placeholder={username.placeholder}
                        value={props.value}
                        maxlength="255"
                        onChange={(e) => { props.setValue(e.target.value) }}
                        isInvalid={username.isInvalid}
                    />

                    {!props.value || username.condition ? "" : <div className="invalid-feedback"> {username.messageDanger} </div>}
                </Form.Group>



            </React.Fragment>
        );
    }
    else {
        return (
            <React.Fragment>
                <Form.Group controlId="Form.Contact.Username.readOnly">
                    <Form.Label>{t('ngen.value')}</Form.Label>
                    <Form.Control readOnly
                        placeholder={t('ngen.contact.placeholder')}
                        name="username" />
                </Form.Group>
            </React.Fragment>
        );
    }
};

export default FormArtifactsSelect;