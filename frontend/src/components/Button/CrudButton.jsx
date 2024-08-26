import React from 'react';
import { Button } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';

// type: {create, read, update, delete}
const CrudButton = ({ type, name, onClick, disabled = false }) => {
  const { t } = useTranslation();

  const button = {
    create: {
      class: 'text-capitalize',
      variant: 'outline-primary',
      title: t('crud.add') + ' ' + name,
      icon: 'fa fa-plus',
      text: t('crud.add') + ' ' + name
    },
    read: {
      class: 'btn-icon btn-rounded',
      variant: 'outline-primary',
      title: t('crud.detail'),
      icon: 'fa fa-eye mx-auto',
      text: ''
    },
    edit: {
      class: 'btn-icon btn-rounded',
      variant: 'outline-warning',
      title: t('crud.edit'),
      icon: 'fa fa-edit',
      text: ''
    },
    delete: {
      class: 'btn-icon btn-rounded',
      variant: 'outline-danger',
      title: t('crud.delete'),
      icon: 'fas fa-trash-alt',
      text: ''
    },
    download: {
      class: 'text-capitalize',
      variant: 'outline-danger',
      title: t('crud.download') + ' ' + name,
      icon: 'fa fa-download',
      text: t('crud.download') + ' ' + name
    }
  };
  return (
    <React.Fragment>
      <Button
        className={button[type].class + ' ' + (disabled ? 'btn-secondary disabled' : '')}
        variant={!disabled ? button[type].variant : ''}
        title={button[type].title}
        disabled={disabled}
        onClick={onClick}
      >
        <i className={button[type].icon} />
        {button[type].text}
      </Button>
    </React.Fragment>
  );
};

export default CrudButton;
