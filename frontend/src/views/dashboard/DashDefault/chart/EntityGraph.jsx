import React, { useEffect, useState } from "react";
import { ResponsivePieCanvas } from "@nivo/pie";
import { Row, Spinner } from "react-bootstrap";

const EntityGraph = ({ list, loading }) => {
  const [entity, setEntity] = useState([]);

  const filtrarEventosNoCero = (datos) => {
    //opino que se debe mostrar aquellas fuentes que este asociados a uno amas eventos
    return datos ? datos.filter((obj) => obj.events.length !== 0) : [];
  };

  useEffect(() => {
    if (list) {
      const filteredData = filtrarEventosNoCero(list);
      setEntity(filteredData);
    }
  }, [list]);

  const data = entity.map((element) => ({
    id: element.name,
    label: element.name,
    value: element.events.length
  }));

  return loading ? (
    <Row className="justify-content-md-center">
      <Spinner animation="border" variant="primary" />
    </Row>
  ) : (
    <div style={{ height: 600 }}>
      <ResponsivePieCanvas
        data={data}
        // margin={{ top: 40, right: 200, bottom: 40, left: 80 }} // margin for the legend
        margin={{ top: 40, right: 40, bottom: 40, left: 80 }}
        innerRadius={0.5}
        padAngle={0.7}
        cornerRadius={3}
        activeOuterRadiusOffset={8}
        colors={{ scheme: "set2" }}
        borderColor={{
          from: "color",
          modifiers: [["darker", 0.6]]
        }}
        arcLinkLabelsSkipAngle={10}
        arcLinkLabelsTextColor="#333333"
        arcLinkLabelsThickness={2}
        arcLinkLabelsColor={{ from: "color" }}
        arcLabelsSkipAngle={10}
        arcLabelsTextColor="#333333"
        defs={[
          {
            id: "dots",
            type: "patternDots",
            background: "inherit",
            color: "rgba(255, 255, 255, 0.3)",
            size: 4,
            padding: 1,
            stagger: true
          },
          {
            id: "lines",
            type: "patternLines",
            background: "inherit",
            color: "rgba(255, 255, 255, 0.3)",
            rotation: -45,
            lineWidth: 6,
            spacing: 10
          }
        ]}
        fill={[
          {
            match: {
              id: "ruby"
            },
            id: "dots"
          },
          {
            match: {
              id: "c"
            },
            id: "dots"
          },
          {
            match: {
              id: "go"
            },
            id: "dots"
          },
          {
            match: {
              id: "python"
            },
            id: "dots"
          },
          {
            match: {
              id: "scala"
            },
            id: "lines"
          },
          {
            match: {
              id: "lisp"
            },
            id: "lines"
          },
          {
            match: {
              id: "elixir"
            },
            id: "lines"
          },
          {
            match: {
              id: "javascript"
            },
            id: "lines"
          }
        ]}
        // legends={[
        //   {
        //     anchor: 'right',
        //     direction: 'column',
        //     justify: false,
        //     translateX: 140,
        //     translateY: 0,
        //     itemsSpacing: 2,
        //     itemWidth: 60,
        //     itemHeight: 14,
        //     itemTextColor: '#999',
        //     itemDirection: 'left-to-right',
        //     itemOpacity: 1,
        //     symbolSize: 14,
        //     symbolShape: 'circle'
        //   }
        // ]}
      />
    </div>
  );
};

export default EntityGraph;
