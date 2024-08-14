import React from 'react'
import { Card } from 'react-bootstrap'
import { NavLink } from 'react-router-dom'

import { API_SERVER } from '../../../config/constant'
import Breadcrumb from '../../../layouts/AdminLayout/Breadcrumb'

import RestLogin from './RestLogin'

import { useTranslation } from 'react-i18next'

const Signin1 = () => {
  const { t } = useTranslation()

  return (
    <React.Fragment>
      <Breadcrumb/>
      <div className="auth-wrapper">
        <div className="auth-content">
          <div className="auth-bg">
            <span className="r"/>
            <span className="r s"/>
            <span className="r s"/>
            <span className="r"/>
          </div>
          <Card className="borderless text-center">
            <Card.Body>
              <div className="mb-4">
                <img src={API_SERVER + 'static/img/ngenlogo_inv.png'} alt="NGEN"
                     className="logo" id="teamlogo_login"/>
              </div>

              <div className="mb-4">
                <i className="feather icon-unlock auth-icon"/>
              </div>

              <RestLogin/>

              <p className="mb-0 text-muted">
                {t('login.do_not_have_an_account')}{' '}
                <NavLink to="/auth/signup" className="f-w-400">
                  {t('button.signup')}
                </NavLink>
              </p>

              <br/>
            </Card.Body>
          </Card>
        </div>
      </div>
    </React.Fragment>
  )
}

export default Signin1
