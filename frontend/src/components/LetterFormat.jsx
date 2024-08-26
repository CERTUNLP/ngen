import React from 'react'
import { Badge } from 'react-bootstrap'

const LetterFormat = ({ useBadge, stringToDisplay, color }) => {
  return (useBadge ?
      <div>
        <Badge className="badge mr-1"
               ref={element => {
                 if (element) {
                   element.style.setProperty('color', '#333', 'important')
                   element.style.setProperty('background', color, 'important')
                 }
               }}>
          {stringToDisplay}
        </Badge>
      </div>
      :
      <div> {stringToDisplay}</div>
  )
}

export default LetterFormat
