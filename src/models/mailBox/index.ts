import { model, Schema } from "mongoose";
import { Coord, MailBox, Track } from "./types";

const coordSchema = new Schema<Coord>({
  x: { type: Number, required: true },
  y: { type: Number, required: true },
});
const trackSchema = new Schema<Track>({
  trackId: { type: String, required: true },
  trackName: { type: String, required: true },
  artistIds: { type: String, required: true },
  artistNames: { type: String, required: true },
  image: { type: String, required: true },
});

const schema = new Schema<MailBox>(
  {
    title: { type: String, required: true },
    imagePath: { type: String, required: false },
    tracks: [trackSchema],
    coord: coordSchema,
    createdAt: { type: String, required: true },
    updatedAt: { type: String, required: true },
  },
  {
    collection: "MailBox",
  }
);

const MailBoxModel = model<MailBox>("MailBox", schema);
export default MailBoxModel;
