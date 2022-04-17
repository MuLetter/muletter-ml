import Express from "express";
import { spawn } from "child_process";
import MailBoxModel from "../models/mailBox";

class IndexRouter {
  router: Express.Router;

  constructor() {
    this.router = Express.Router();
    this.SetRoutes();
  }

  SetRoutes() {
    // New MailBox 생성알림
    this.router.post(
      "/",
      async (req: Express.Request, res: Express.Response) => {
        try {
          const { id } = req.body;
          const mailBox = await MailBoxModel.findById(id);

          if (mailBox) {
            const _id = mailBox._id;

            const writingProcess = spawn("python3", ["python", _id.toString()]);

            writingProcess.stdout.on("data", (data) => {
              console.log(`[ML Program Message] ${data.toString()}`);
            });
            writingProcess.stderr.on("data", (data) => {
              console.log(`[ML Program Error Message] ${data.toString()}`);
            });

            return res.status(200).json({
              message: `Thanks for letting me know. I'll write a letter for ${_id}`,
            });
          } else {
            return res.status(404).json({
              message: "MailBox Not Found :(",
            });
          }
        } catch (err) {
          console.error(err);
          return res.status(500).json({
            message: "Sorry :( It's Server Error.",
          });
        }
      }
    );
  }
}

export default new IndexRouter().router;
