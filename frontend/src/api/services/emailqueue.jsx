import apiInstance from "../api";
import { COMPONENT_URL } from "config/constant";
import setAlert from "utils/setAlert";

const getEmailMessages = async (currentPage, filters = "", order = "-created") => {
  try {
    const response = await apiInstance.get(
      `${COMPONENT_URL.emailmessage}?page=${currentPage}&ordering=${order}&${filters}`
    );
    return response;
  } catch (error) {
    const message = error?.response?.data?.detail || "Failed to fetch email messages";
    setAlert(message, "error");
    throw error;
  }
};

const sendQueuedEmail = async (id) => {
  try {
    const response = await apiInstance.post(`${COMPONENT_URL.emailmessage}${id}/send/`);
    return response.data;
  } catch (error) {
    const message = error?.response?.data?.error || "Failed to dispatch email";
    setAlert(message, "error");
    throw error;
  }
};

const resendEmail = async (id) => {
  try {
    const response = await apiInstance.post(`${COMPONENT_URL.emailmessage}${id}/resend/`);
    return response.data;
  } catch (error) {
    const message = error?.response?.data?.error || "Failed to resend email";
    setAlert(message, "error");
    throw error;
  }
};

const sendAllPending = async () => {
  try {
    const response = await apiInstance.post(`${COMPONENT_URL.emailmessage}send_all_pending/`);
    return response.data;
  } catch (error) {
    const message = error?.response?.data?.error || "Failed to dispatch all pending emails";
    setAlert(message, "error");
    throw error;
  }
};

const getEmailQueueStats = async () => {
  try {
    const response = await apiInstance.get(`${COMPONENT_URL.emailmessage}stats/`);
    return response.data;
  } catch (error) {
    const message = error?.response?.data?.detail || "Failed to fetch queue stats";
    setAlert(message, "error");
    throw error;
  }
};

export { getEmailMessages, sendQueuedEmail, resendEmail, sendAllPending, getEmailQueueStats };
