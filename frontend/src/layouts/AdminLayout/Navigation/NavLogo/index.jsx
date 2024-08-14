import React, { useContext } from 'react'
import { Link } from 'react-router-dom'
import { API_SERVER } from '../../../../config/constant';

import { ConfigContext } from '../../../../contexts/ConfigContext'
import * as actionType from '../../../../store/actions'

const NavLogo = () => {
  const configContext = useContext(ConfigContext)
  const { collapseMenu } = configContext.state
  const { dispatch } = configContext

  let toggleClass = ['mobile-menu']
  if (collapseMenu) {
    toggleClass = [...toggleClass, 'on']
  }

  return (
    <React.Fragment>
      <div className="navbar-brand header-logo">
        <Link to="#" className="b-brand">
          <img src={API_SERVER + 'static/img/ngenlogo_inv_light.png'} alt="NGEN" className="logo" id="teamlogo"/>
        </Link>
        <Link to="#" className={toggleClass.join(' ')} id="mobile-collapse"
              onClick={() => dispatch({ type: actionType.COLLAPSE_MENU })}>
          <span/>
        </Link>
      </div>
    </React.Fragment>
  )
}

export default NavLogo
