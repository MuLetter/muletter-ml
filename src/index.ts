import App from "./App";
import dotenv from "dotenv";
import mongooseInit from "./models";

dotenv.config();

(async function () {
  await mongooseInit();
})();

App;
