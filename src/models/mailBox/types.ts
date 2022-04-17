import { Document, Types } from "mongoose";

export interface Track {
  trackId: string;
  trackName: string;
  artistIds: string;
  artistNames: string;
  image: string;
}

export type Coord = {
  x: number;
  y: number;
};

export type MailBox = {
  title: string;
  imagePath?: string;
  tracks: Track[];
  coord?: Coord;
  createdAt: string;
  updatedAt: string;
};
