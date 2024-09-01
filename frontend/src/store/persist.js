import { persistStore } from "redux-persist";
import store from "./index";

const persist = persistStore(store);

export default persist;
