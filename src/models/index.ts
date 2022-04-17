import { connect } from "mongoose";

export default async function mongooseInit() {
  const { MONGO_HOST, MONGO_PORT, MONGO_APP } = process.env;
  const connectURL = `mongodb://${MONGO_HOST}:${MONGO_PORT}/${MONGO_APP}`;
  await connect(connectURL);

  console.log("[mongoose] connected :)");
}
