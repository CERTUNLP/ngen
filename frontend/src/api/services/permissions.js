import  apiInstance  from "../api";

const getPermission = (url) => {
    return apiInstance.get(url);
}

export {getPermission}