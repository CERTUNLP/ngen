import React, { useEffect, useState } from "react";
import { Card } from "react-bootstrap";

import { getMinifiedState } from "../../../../api/services/states";
import { getMinifiedUser } from "../../../../api/services/users";
import TableCase from "../../../case/components/TableCase";
import { useTranslation } from "react-i18next";

const DashboardCases = ({ list, loading }) => {
  const [userNames, setUserNames] = useState({});
  const [stateNames, setStateNames] = useState({});

  const { t } = useTranslation();

  useEffect(() => {
    getMinifiedUser()
      .then((response) => {
        let dicUser = {};
        response.forEach((user) => {
          dicUser[user.url] = user.username;
        });
        setUserNames(dicUser);
      })
      .catch((error) => {
        console.log(error);
      });

    getMinifiedState().then((response) => {
      let dicState = {};
      response.forEach((state) => {
        dicState[state.url] = state.name;
      });
      setStateNames(dicState);
    });
  }, [list]);

  return (
    <div>
      <Card>
        <Card.Header>
          <Card.Title as="h5">{t("case.last10")}</Card.Title>
        </Card.Header>
        <TableCase
          cases={list}
          loading={loading}
          disableCheckbox={true}
          disableDate={true}
          disableName={true}
          disablePriority={true}
          disableTlp={true}
          stateNames={stateNames}
          userNames={userNames}
          editColum={false}
          deleteColum={false}
          detailModal={false}
          navigationRow={false}
          selectCase={true}
          disableNubersOfEvents={false}
          disableUuid={true}
          disableDateModified={true}
          disableEvents={true}
        />
      </Card>
    </div>
  );
};

export default DashboardCases;
