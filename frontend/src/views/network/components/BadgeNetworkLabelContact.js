import React from 'react';
import { Badge } from 'react-bootstrap';
import { useState, useEffect } from 'react';
import { getContact } from '../../../api/services/contacts';
import { useTranslation, Trans } from 'react-i18next';

const BadgeNetworkLabelContact = (props) => {
    const [contact, setContact] = useState('');
    const { t } = useTranslation();

    useEffect(() => {

        showContactData(props.url)

    }, []);

    const showContactData = (url) => {
        getContact(url)
            .then((response) => {
                console.log(response)
                setContact(response.data)
            })
            .catch();
    }

    const labelRole =
    {
        technical: `${t('ngen.role.technical')}`,
        administrative: `${t('ngen.role.administrative')}`,
        abuse: `${t('ngen.role.abuse')}`,
        notifications: `${t('ngen.role.notifications')}`,
        noc: `${t('ngen.role.noc')}`,
    };

    return (
        contact &&
        <React.Fragment>
            <Badge pill variant='info' className="mr-1">
                {contact.name + ' (' + labelRole[`${contact.role}`] + ')'}</Badge>
            <br />
        </React.Fragment>
    );
};

export default BadgeNetworkLabelContact;
//<Form.Control plaintext readOnly defaultValue={contact.name + ' (' + contact.role + '): ' + contact.username} />
