import NVD3Chart from 'react-nvd3';
import React, { useState, useEffect } from 'react'
import { useTranslation, Trans } from 'react-i18next';


const EntityGraph = ({ list }) => {

    const [entity, setEntity] = useState([]);

    const filtrarEventosNoCero = (datos) => { //opino que se debe mostrar aquellas fuentes que este asociados a uno amas eventos 
        return datos.filter((objeto) => objeto.eventCount !== 0);
    };

    useEffect(() => {
        setEntity(filtrarEventosNoCero(list))

    }, [list])
    const { t } = useTranslation();
                console.log(entity);
    return (
        <div>
            {
                entity.length > 0 ? <NVD3Chart id="chart" height={600} type="pieChart" datum={entity} x="name" y="eventCount" labelType="percent" /> :
                    t('ngen.dashboard.no_events_associated_with_entities')

            }
        </div>
    );
}

export default EntityGraph