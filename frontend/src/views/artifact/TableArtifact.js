import React from 'react'
import { Card, Table } from 'react-bootstrap';
import { Link } from 'react-router-dom'
import CrudButton from '../../components/Button/CrudButton';
import { useTranslation } from 'react-i18next';

const TableArtifact = ({ artifact }) => {
  const { t } = useTranslation();

  return (
    <div>
      <Card>
        <Card.Body>
          <ul className="list-group my-4">
            <Table responsive hover>
              <thead>
              <tr>
                <th>#</th>
                <th>{t('ngen.type')}</th>
                <th>{t('ngen.value')}</th>
                <th>{t('ngen.related')}</th>
              </tr>
              </thead>
              <tbody>
              {artifact.map((artefact, index) => {
                return (
                  <tr>
                    <th>{index + 1}</th>
                    <td>{artefact.tipe}</td>
                    <td>{artefact.value}</td>
                    <td>{artefact.related}</td>

                    <td>
                      <CrudButton type='read' onClick=""/>

                      <Link to="">
                        <CrudButton type='edit'/>
                      </Link>
                      <CrudButton type='delete' onClick=""/>
                    </td>

                  </tr>
                )
              })}

              </tbody>
            </Table>
          </ul>
        </Card.Body>
      </Card>
    </div>
  )
}

export default TableArtifact
