import React, { useState } from "react";
import { Row, Spinner, Table } from "react-bootstrap";
import CrudButton from "../../../components/Button/CrudButton";
import { deleteNetwork, getNetwork, isActive } from "../../../api/services/networks";
import BadgeNetworkLabelContact from "./BadgeNetworkLabelContact";
import ModalConfirm from "../../../components/Modal/ModalConfirm";
import ActiveButton from "../../../components/Button/ActiveButton";
import ModalDetailNetwork from "./ModalDetailNetwork";
import Ordering from "../../../components/Ordering/Ordering";
import { useTranslation } from "react-i18next";

const TableNetwork = ({ setIsModify, list, loading, order, setOrder, setLoading, currentPage, entityNames, basePath = "" }) => {
  const { t } = useTranslation();
  const [network, setNetwork] = useState("");

  const [modalDelete, setModalDelete] = useState(false);
  const [modalState, setModalState] = useState(false);
  const [modalShow, setModalShow] = useState(false);

  const [url, setUrl] = useState(null);
  const [cidr, setCidr] = useState(null);
  const [domain, setDomain] = useState(null);
  const [active, setActive] = useState(null);
  const [id, setId] = useState("");

  if (loading) {
    return (
      <Row className="justify-content-md-center">
        <Spinner animation="border" variant="primary" />
      </Row>
    );
  }

  //Read Network
  const showNetwork = (url) => {
    setId(url.split("/")[url.split("/").length - 2]);
    setUrl(url);
    setNetwork("");
    getNetwork(url)
      .then((response) => {
        setNetwork(response.data);
        setModalShow(true);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  //Update Network
  const pressActive = (domain, cidr, active, url) => {
    setUrl(url);
    setCidr(cidr);
    setDomain(domain);
    setActive(active);
    setModalState(true);
  };
  const switchState = (url, state, name) => {
    isActive(url, !state, name)
      .then((response) => {
        setIsModify(response);
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        setModalState(false);
        setModalShow(false);
      });
  };

  //Remove Network
  const Delete = (url, cidr, domain) => {
    setUrl(url);
    setCidr(cidr);
    setDomain(domain);
    setModalDelete(true);
  };

  const removeNetwork = (url) => {
    deleteNetwork(url, cidr || domain)
      .then((response) => {
        setIsModify(response);
      })
      .catch((error) => {
        console.log(error);
      })
      .finally(() => {
        setModalDelete(false);
      });
  };
  const letterSize = { fontSize: "1.1em" };

  return (
    <React.Fragment>
      <Table responsive hover className="text-center">
        <thead>
          <tr>
            <Ordering
              field="address_value"
              label={t("ngen.addressvalue")}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <Ordering
              field="domain"
              label={t("ngen.domain")}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <Ordering
              field="cidr"
              label={t("ngen.cidr")}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <Ordering
              field="type"
              label={t("ngen.type")}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <Ordering
              field="active"
              label={t("ngen.active")}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <Ordering
              field="network_entity__name"
              label={t("ngen.entity")}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <Ordering
              field="contact_count"
              label={t("ngen.contact_other")}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <Ordering
              field="children_count"
              label={t("ngen.children")}
              order={order}
              setOrder={setOrder}
              setLoading={setLoading}
              letterSize={letterSize}
            />
            <th style={letterSize}>{t("ngen.action_one")}</th>
            <th style={letterSize}></th>
          </tr>
        </thead>
        <tbody>
          {list.map((network, index) => {
            const parts = network.url.split("/");
            let itemNumber = parts[parts.length - 2];
            return (
              <tr key={index}>
                <td>{network.address_value}</td>
                <td>{network.domain}</td>
                <td>{network.cidr}</td>
                <td>{network.type === "internal" ? t("ngen.network.type.internal") : t("ngen.network.type.external")}</td>
                <td>
                  <ActiveButton
                    active={network.active}
                    onClick={() => pressActive(network.domain, network.cidr, network.active, network.url)}
                    permissions="change_network"
                  />
                </td>
                <td>{network.network_entity ? entityNames[network.network_entity] : "-"}</td>
                <td>
                  {network.contacts?.length > 0 ? network.contacts.map((contactItem, index) => {
                    return <BadgeNetworkLabelContact url={contactItem} key={index} />;
                  }) : "-"}
                </td>
                <td>{network.children.length}</td>
                <td>
                  <CrudButton type="read" onClick={() => showNetwork(network.url)} />
                  <CrudButton type="edit" to={`${basePath}/networks/edit/${itemNumber}`} checkPermRoute />
                  <CrudButton
                    type="delete"
                    onClick={() => Delete(network.url, network.cidr, network.domain)}
                    permissions="delete_network"
                  />
                </td>
              </tr>
            );
          })}
        </tbody>
      </Table>
      <ModalDetailNetwork show={modalShow} network={network} onHide={() => setModalShow(false)} id={id} />
      <ModalConfirm
        type="delete"
        component="Red"
        name={cidr || domain}
        showModal={modalDelete}
        onHide={() => setModalDelete(false)}
        ifConfirm={() => removeNetwork(url)}
      />
      <ModalConfirm
        type="editState"
        component="Red"
        name={cidr || domain}
        state={active}
        showModal={modalState}
        onHide={() => setModalState(false)}
        ifConfirm={() => switchState(url, active, cidr)}
      />
    </React.Fragment>
  );
};

export default TableNetwork;
